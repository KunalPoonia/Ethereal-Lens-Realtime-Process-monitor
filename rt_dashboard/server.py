# ─── Server ──────────────────────────────────────────────────────────
# FastAPI backend — REST endpoints + WebSocket live stream.

import asyncio
import os
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.datastore import DataStore
from core.poller import Poller

# ─── App setup ───────────────────────────────────────────────────────

app = FastAPI(title="Process Monitor")

app.mount("/static", StaticFiles(directory="static"), name="static")

store  = DataStore()
poller = Poller(store)

# ─── Aliases & constants ─────────────────────────────────────────────

_COMMAND_ALIASES = {
    "vs code":    "code",
    "vscode":     "code",
    "open code":  "code",
    "word":       "winword",
    "powerpoint": "powerpnt",
    "edge":       "msedge",
}

_START_MENU_PATHS = [
    Path(os.environ.get("APPDATA",      "")) / r"Microsoft\Windows\Start Menu\Programs",
    Path(os.environ.get("PROGRAMDATA",  "")) / r"Microsoft\Windows\Start Menu\Programs",
]

# ─── Pydantic models ─────────────────────────────────────────────────

class RunTaskRequest(BaseModel):
    command: str

class EndTaskRequest(BaseModel):
    pids: list[int]
    name: str = ""

# ─── Lifecycle ───────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    poller.start()

@app.on_event("shutdown")
async def shutdown_event():
    poller.stop()

# ─── Helpers ─────────────────────────────────────────────────────────

def _find_start_menu_shortcut(query: str) -> Optional[str]:
    """Search Windows Start Menu for the closest matching .lnk shortcut."""
    q = query.lower()
    matches = []

    for base in _START_MENU_PATHS:
        if not base.exists():
            continue
        try:
            for lnk in base.rglob("*.lnk"):
                stem = lnk.stem.lower()
                if "uninstall" in stem:
                    continue
                if q in stem:
                    matches.append(lnk)
        except Exception:
            pass

    if not matches:
        return None

    def _score(p: Path) -> int:
        stem = p.stem.lower()
        if stem == q:         return 0
        if stem.startswith(q): return 1
        return len(stem)

    matches.sort(key=_score)
    return str(matches[0])


def _current_snapshot() -> dict:
    """Return a serialisable snapshot of the current store state."""
    with store.lock():
        return {
            "timestamp": datetime.now().isoformat(),
            "performance": {
                "cpu_percent":        round(store.cpu_percent,    1),
                "ram_used_gb":        round(store.ram_used,       2),
                "ram_total_gb":       round(store.ram_total,      2),
                "ram_percent":        round(store.ram_percent,    1),
                "disk_read_rate_mbps":  round(store.disk_read_rate,  2),
                "disk_write_rate_mbps": round(store.disk_write_rate, 2),
                "net_sent_rate_kbps":   round(store.net_sent_rate,   2),
                "net_recv_rate_kbps":   round(store.net_recv_rate,   2),
            },
            "processes": [
                {
                    "name":      p.get("name",     ""),
                    "pid":       p.get("pid",       0),
                    "pids":      p.get("pids",     []),
                    "cpu":       p.get("cpu",       0),
                    "memory_mb": p.get("memory",    0),
                    "status":    p.get("status",   ""),
                    "category":  p.get("category", ""),
                    "threads":   p.get("threads",   0),
                }
                for p in store.processes
            ],
            "summary": {
                "total_processes": len(store.processes),
                "apps":       sum(1 for p in store.processes if p.get("category") == "app"),
                "background": sum(1 for p in store.processes if p.get("category") != "app"),
            },
        }

# ─── Routes ──────────────────────────────────────────────────────────

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


@app.post("/api/run-task")
async def run_task(req: RunTaskRequest):
    original = req.command.strip()
    if not original:
        return {"status": "error", "message": "No command provided."}

    command = _COMMAND_ALIASES.get(original.lower(), original)
    candidates = [command]
    if not command.lower().endswith(".exe") and "." not in command:
        candidates.append(f"{command}.exe")

    # Strategy 1: os.startfile — handles UWP, App Paths, URLs, files
    for cmd in candidates:
        try:
            os.startfile(cmd)
            return {"status": "ok", "message": f"'{original}' launched successfully."}
        except OSError:
            pass

    # Strategy 2: Start Menu shortcut search
    lnk = _find_start_menu_shortcut(original)
    if lnk:
        try:
            os.startfile(lnk)
            return {"status": "ok", "message": f"'{original}' launched successfully."}
        except OSError:
            pass

    # Strategy 3: shell 'start' command
    try:
        subprocess.Popen(
            f'start "" "{command}"', shell=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return {"status": "ok", "message": f"'{original}' launched successfully."}
    except Exception:
        pass

    # Strategy 4: direct subprocess (supports arguments)
    try:
        subprocess.Popen(
            command, shell=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        return {"status": "ok", "message": f"'{original}' launched successfully."}
    except Exception as e:
        return {"status": "error", "message": f"Could not launch '{original}': {e}"}


@app.get("/api/snapshot")
async def snapshot_system():
    data = _current_snapshot()
    filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/end-task")
async def end_task(req: EndTaskRequest):
    killed = denied = 0

    for pid in req.pids:
        try:
            psutil.Process(pid).terminate()
            killed += 1
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied:
            denied += 1
        except Exception:
            continue

    label = req.name or f"{len(req.pids)} process{'es' if len(req.pids) != 1 else ''}"

    if killed > 0 and denied == 0:
        return {"status": "ok",    "message": f"'{label}' terminated ({killed} process{'es' if killed > 1 else ''})."}
    if killed > 0:
        return {"status": "ok",    "message": f"'{label}': {killed} terminated, {denied} access denied."}
    if denied > 0:
        return {"status": "error", "message": f"Access denied — cannot terminate '{label}'. Try running as Administrator."}
    return     {"status": "error", "message": f"No running processes found for '{label}'."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Stream live metrics to the frontend at ~1 Hz."""
    await websocket.accept()
    try:
        while True:
            with store.lock():
                frame = {
                    "cpu_percent":      store.cpu_percent,
                    "ram_percent":      store.ram_percent,
                    "ram_used":         store.ram_used,
                    "ram_total":        store.ram_total,
                    "disk_read_rate":   store.disk_read_rate,
                    "disk_write_rate":  store.disk_write_rate,
                    "disk_total_rate":  store.disk_total_rate,
                    "net_sent_rate":    store.net_sent_rate,
                    "net_recv_rate":    store.net_recv_rate,
                    "cpu_history":      list(store.cpu_history),
                    "ram_history":      list(store.ram_history),
                    "disk_history":     list(store.disk_history),
                    "net_sent_history": list(store.net_sent_history),
                    "net_recv_history": list(store.net_recv_history),
                    "boot_time":        psutil.boot_time(),
                    "processes":        store.processes,
                }
            await websocket.send_json(frame)
            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
