import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.datastore import DataStore
from core.poller import Poller

app = FastAPI(title="Process Monitor Backend")

# Mount the static directory to serve HTML, CSS, and JS
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
                    "net_sent_rate": store.net_sent_rate,
                    "net_recv_rate": store.net_recv_rate,
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
