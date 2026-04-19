# ⚡ Real-Time Process Monitor

A modern, browser-based system monitor built with **FastAPI**, **WebSockets**, and **Tailwind CSS**. Streams live CPU, RAM, Disk, and Network metrics alongside a full process manager — all rendered in a sleek, minimal dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 📋 Processes View
- **Live process table** — Name, Status, CPU%, Memory, Disk I/O, Network, grouped by Apps and Background Processes
- **Collapsible sections** — toggle Apps and Background process groups independently
- **Search & filter** — find any process instantly by name, publisher, or PID
- **Run new task** — launch any application, command, or UWP app from the dashboard (supports Start Menu shortcut resolution)
- **End task** — terminate selected processes with a confirmation modal and toast feedback
- **Sort controls** — sort by CPU or Memory via the dropdown menu
- **Deterministic PID tracking** — selected rows persist across data refreshes
- **1-second polling** — auto-refreshes with zero flicker or scroll reset

### 📈 Performance View
- **Live bar-chart graphs** for CPU and Memory — 60-point rolling history with opacity-graded bars (older = faded, recent = vivid)
- **CPU card** — current %, delta change indicator (↗/↘), and session peak value
- **Memory card** — used/total GB with utilization percentage
- **Disk I/O card** — real-time Read and Write rates (MB/s)
- **Network card** — live Download and Upload rates (KB/s)
- **Bento grid layout** — responsive 2×2 card arrangement with glass-morphic styling

### 📸 System Snapshot
- **One-click export** — captures a complete freeze-frame of CPU, RAM, Disk, Network, and every running process
- **JSON download** — timestamped file with hostname, platform info, performance metrics, and full process list
- **Use cases** — benchmarking, bug reports, forensics, trend tracking over time

### 🎨 Theming
- **Light / Dark mode** — toggle with the theme button in the navbar, persists via `localStorage`
- **"Ethereal Observer" design language** — deep navy dark mode (`#0f0c19`) with lavender accents, warm cream light mode
- **Glass-card effects** — backdrop blur, subtle borders, smooth hover animations
- **Material Design icons** — Google Material Symbols throughout

---

## 🏗️ Architecture

```
Real-time Process monitor/
├── requirements.txt            # Python dependencies
├── run.bat                     # One-click launcher (Windows)
└── rt_dashboard/
    ├── server.py               # FastAPI app — REST API + WebSocket streaming
    ├── config.py               # Poll intervals, history length, theme palettes
    ├── core/
    │   ├── poller.py           # Background threads — stats + process enumeration
    │   └── datastore.py        # Thread-safe shared state with rolling deques
    └── static/
        ├── index.html          # Dashboard UI (Tailwind CSS)
        ├── app.js              # WebSocket client, DOM rendering, interactivity
        ├── style.css           # Custom CSS — animations, dark mode overrides
        └── theme.js            # Dynamic CSS variable injection (light/dark palettes)
```

### Data Flow

```
┌──────────────┐    psutil     ┌──────────────┐   Thread Lock   ┌──────────────┐
│  StatsPoller │──────────────▸│   DataStore  │◂──────────────▸│ProcessPoller │
│  (1s loop)   │   CPU/RAM/    │  (deques +   │                │ (child proc) │
│              │   Disk/Net    │   snapshots)  │  process list  │              │
└──────────────┘               └──────┬───────┘                └──────────────┘
                                      │
                               WebSocket /ws
                               (JSON, 1s push)
                                      │
                                      ▼
                               ┌──────────────┐
                               │   Browser    │
                               │  (app.js)    │
                               │  Bar graphs  │
                               │  Process tbl │
                               └──────────────┘
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serve the dashboard UI |
| `WS` | `/ws` | Stream live metrics (CPU, RAM, Disk, Net, processes, history arrays) |
| `POST` | `/api/run-task` | Launch a new process (`{"command": "notepad"}`) |
| `POST` | `/api/end-task` | Terminate processes by PID list (`{"pids": [1234], "name": "..."}`) |
| `GET` | `/api/snapshot` | Download a JSON freeze-frame of the full system state |

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Windows OS** (uses `ctypes.windll` for window enumeration)

### Installation

```bash
# Clone the repo
git clone https://github.com/KunalPoonia/Ethereal-Lens-Realtime-Process-monitor.git
cd Ethereal-Lens-Realtime-Process-monitor

# Install dependencies
pip install -r requirements.txt
```

### Run

**Option A — Batch file:**
```bash
run.bat
```

**Option B — Manual:**
```bash
cd rt_dashboard
uvicorn server:app --reload
```

Then open **http://127.0.0.1:8000** in your browser.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Async web framework — REST API + WebSocket |
| `uvicorn` | ASGI server to run FastAPI |
| `psutil` | System metrics & process enumeration |
| `websockets` | WebSocket protocol support |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, FastAPI, uvicorn |
| **System Metrics** | psutil, ctypes (Win32 API) |
| **Data Transport** | WebSocket (1s push interval) |
| **Frontend** | HTML5, Vanilla JavaScript |
| **Styling** | Tailwind CSS (CDN), Custom CSS |
| **Fonts** | Space Grotesk (headlines), Manrope (body) |
| **Icons** | Google Material Symbols Outlined |
| **Concurrency** | threading, multiprocessing (process poller runs in child process) |

---

## 📝 License

This project is licensed under the MIT License.
