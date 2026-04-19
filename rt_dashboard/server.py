import asyncio
import psutil
import subprocess
import os
import signal
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core.datastore import DataStore
from core.poller import Poller

app = FastAPI(title="Process Monitor Backend")


class RunTaskRequest(BaseModel):
    command: str


class EndTaskRequest(BaseModel):
    pids: list[int]
    name: str = ""


# Mount the static directory to serve HTML, CSS, and JS
# NOTE: This must come AFTER the API route definitions below, but FastAPI
# handles path-based routing, so we define API routes before the mount.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize our shared state and background poller
store = DataStore()
poller = Poller(store)

@app.on_event("startup")
async def startup_event():
    """Start the background hardware monitoring threads when the server boots."""
    poller.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanly shut down the background threads when stopping the server."""
    poller.stop()

@app.get("/")
async def serve_index():
    """Serve the main dashboard UI."""
    return FileResponse("static/index.html")


from pathlib import Path

def find_start_menu_shortcut(query: str) -> str | None:
    """Searches Windows Start Menu structures for the closest matching .lnk application shortcut."""
    paths = [
        Path(os.environ.get('APPDATA', '')) / r"Microsoft\Windows\Start Menu\Programs",
        Path(os.environ.get('PROGRAMDATA', '')) / r"Microsoft\Windows\Start Menu\Programs"
    ]
    query = query.lower()
    matches = []
    
    for base_path in paths:
        if not base_path.exists():
            continue
        try:
            for lnk_path in base_path.rglob("*.lnk"):
                stem = lnk_path.stem.lower()
                # Exclude uninstallation shortcuts
                if "uninstall" in stem:
                    continue
                if query in stem:
                    matches.append(lnk_path)
        except Exception:
            # Handle possible OS access restrictions during iteration
            pass
            
    if not matches:
        return None
        
    # Score matches to prioritize exact matches, then prefixes, then shortest overall string
    def score(p: Path):
        stem = p.stem.lower()
        if stem == query: return 0
        if stem.startswith(query): return 1
        return len(stem)
        
    matches.sort(key=score)
    return str(matches[0])

@app.post("/api/run-task")
async def run_task(req: RunTaskRequest):
    """Launch a new process from a command string."""
    original_command = req.command.strip()
    if not original_command:
        return {"status": "error", "message": "No command provided."}
    
    # 1. Expand common human aliases
    c_lower = original_command.lower()
    mappings = {
        "vs code": "code",
        "vscode": "code",
        "open code": "code",
        "word": "winword",
        "powerpoint": "powerpnt",
        "edge": "msedge",
    }
    command = mappings.get(c_lower, original_command)

    # Automatically appending .exe triggers Windows App Paths registry resolution natively.
    # So "steam.exe" will magically resolve even if Steam isn't strictly in the PATH.
    tests = [command]
    if not command.lower().endswith('.exe') and '.' not in command:
        tests.append(f"{command}.exe")

    # Strategy 1: Try os.startfile — works for UWP apps (calc, ms-settings:), 
    # files, folders, URLs, and most executables via App Paths
    for cmd in tests:
        try:
            os.startfile(cmd)
            return {"status": "ok", "message": f"Task '{original_command}' launched successfully."}
        except OSError:
            pass

    # Strategy 2: Search Windows Start Menu shortcuts
    # This emulates the natural behavior of the Windows Search bar
    match_lnk = find_start_menu_shortcut(original_command)
    if match_lnk:
        try:
            os.startfile(match_lnk)
            return {"status": "ok", "message": f"Task '{original_command}' launched successfully."}
        except OSError:
            pass
    
    # Strategy 2: Try 'start' shell command — handles many Windows-specific cases
    try:
        subprocess.Popen(
            f'start "" "{command}"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {"status": "ok", "message": f"Task '{command}' launched successfully."}
    except Exception:
        pass
    
    # Strategy 3: Direct execution — handles commands with arguments (e.g. "python script.py")
    try:
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        return {"status": "ok", "message": f"Task '{command}' launched successfully."}
    except Exception as e:
        return {"status": "error", "message": f"Could not launch '{command}': {str(e)}"}


@app.get("/api/snapshot")
async def snapshot_system():
    """Capture a complete freeze-frame of the current system state."""
    from datetime import datetime
    import platform

    with store.lock():
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "hostname": platform.node(),
            "platform": platform.platform(),
            "performance": {
                "cpu_percent": round(store.cpu_percent, 1),
                "ram_used_gb": round(store.ram_used, 2),
                "ram_total_gb": round(store.ram_total, 2),
                "ram_percent": round(store.ram_percent, 1),
                "disk_read_rate_mbps": round(store.disk_read_rate, 2),
                "disk_write_rate_mbps": round(store.disk_write_rate, 2),
                "net_sent_rate_kbps": round(store.net_sent_rate, 2),
                "net_recv_rate_kbps": round(store.net_recv_rate, 2),
            },
            "processes": [
                {
                    "name": p.get("name", ""),
                    "pid": p.get("pid", 0),
                    "pids": p.get("pids", []),
                    "cpu": p.get("cpu", 0),
                    "memory_mb": p.get("memory", 0),
                    "status": p.get("status", ""),
                    "category": p.get("category", ""),
                    "threads": p.get("threads", 0),
                }
                for p in store.processes
            ],
            "summary": {
                "total_processes": len(store.processes),
                "apps": sum(1 for p in store.processes if p.get("category") == "app"),
                "background": sum(1 for p in store.processes if p.get("category") != "app"),
            }
        }

    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=snapshot,
        headers={
            "Content-Disposition": f'attachment; filename="snapshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        }
    )


@app.post("/api/end-task")
async def end_task(req: EndTaskRequest):
    """Terminate all processes in a group by their PIDs."""
    import psutil
    killed = 0
    denied = 0
    for pid in req.pids:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            killed += 1
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied:
            denied += 1
        except Exception:
            continue
    
    label = req.name or f"{len(req.pids)} processes"
    if killed > 0 and denied == 0:
        return {"status": "ok", "message": f"'{label}' terminated ({killed} process{'es' if killed > 1 else ''})."}
    elif killed > 0 and denied > 0:
        return {"status": "ok", "message": f"'{label}': {killed} terminated, {denied} access denied."}
    elif denied > 0:
        return {"status": "error", "message": f"Access denied — cannot terminate '{label}'. Try running as Administrator."}
    else:
        return {"status": "error", "message": f"No running processes found for '{label}'."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Stream live system metrics to the frontend via WebSockets.
    Pushes an update roughly every 1000ms.
    """
    await websocket.accept()
    try:
        while True:
            # Safely grab a snapshot of the current state using the thread lock
            with store.lock():
                state = {
                    "cpu_percent": store.cpu_percent,
                    "ram_percent": store.ram_percent,
                    "ram_used": store.ram_used,
                    "ram_total": store.ram_total,
                    "disk_read_rate": store.disk_read_rate,
                    "disk_write_rate": store.disk_write_rate,
                    "disk_total_rate": store.disk_total_rate,
                    "net_sent_rate": store.net_sent_rate,
                    "net_recv_rate": store.net_recv_rate,
                    "eth_usage_pct": store.eth_usage_pct,
                    "wifi_usage_pct": store.wifi_usage_pct,
                    "eth_sent_rate": store.eth_sent_rate,
                    "eth_recv_rate": store.eth_recv_rate,
                    "wifi_sent_rate": store.wifi_sent_rate,
                    "wifi_recv_rate": store.wifi_recv_rate,
                    "eth_adapter_name": store.eth_adapter_name,
                    "wifi_adapter_name": store.wifi_adapter_name,
                    "cpu_name": store.cpu_name,
                    "cpu_history": list(store.cpu_history),
                    "ram_history": list(store.ram_history),
                    "disk_history": list(store.disk_history),
                    "net_sent_history": list(store.net_sent_history),
                    "net_recv_history": list(store.net_recv_history),
                    "eth_total_history": list(store.eth_total_history),
                    "wifi_total_history": list(store.wifi_total_history),
                    "gpus": list(store.gpus),
                    "boot_time": psutil.boot_time(),
                    "processes": store.processes
                }
            
            # Broadcast the snapshot as JSON
            await websocket.send_json(state)
            
            # Wait 1 second before sending the next frame
            await asyncio.sleep(1.0)
            
    except WebSocketDisconnect:
        # Expected behavior when a user closes the browser tab
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
