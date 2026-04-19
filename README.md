# ⚡ Ethereal Lens — Real-Time Process Monitor

A modern, browser-based system monitor built with **FastAPI**, **WebSockets**, and **Tailwind CSS**. Streams live CPU, RAM, Disk, Network, and GPU metrics alongside a full process manager — all rendered in a premium glassmorphic dashboard with ambient lighting, animated tab transitions, and a hoverable performance sidebar.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 📋 Processes View
- **Live process table** — Name, Status, CPU%, Memory, Disk I/O, Network, grouped by Apps and Background Processes
- **Collapsible sections** — toggle Apps and Background process groups independently
- **Search & filter** — find any process instantly by name or PID
- **Advanced filter presets** — one-click filters for All, Active Only, High CPU/Memory, and System Processes
- **Run new task** — launch any application, command, or UWP app from a styled modal (supports Start Menu shortcut resolution and human aliases like "vscode")
- **End task** — terminate selected processes via a confirmation modal with critical system process detection (warns before killing `csrss`, `lsass`, `svchost`, etc.)
- **Context-aware status badges** — dynamic Stable / Warning / Critical badges based on real-time CPU and memory thresholds (not just process status)
- **Smart process icons** — auto-detected icons for browsers, code editors, music apps, and system services
- **Deterministic PID tracking** — selected rows persist across data refreshes (uses lowest PID in group)
- **Process grouping** — identical process names are merged into a single row with aggregated CPU, memory, threads, and PID list
- **Utility bar** — Run New Task, End Task, Filter dropdown, and More menu (Refresh, Collapse All, Expand All, Clear Selection)
- **1-second WebSocket push** — auto-refreshes with zero flicker, scroll reset, or DOM thrashing

### 📈 Performance View
- **Live bar-chart graphs** for CPU and Memory — 20-point rolling history with opacity-graded bars (older = faded, recent = vivid)
- **CPU card** — current %, session peak, and rolling average
- **Memory card** — used/total GB with utilization percentage, peak, and average
- **Disk I/O card** — real-time Read and Write rates (MB/s) with health status indicator
- **Network card** — live Download and Upload rates (KB/s) with latency display
- **Bento grid layout** — responsive 4-column card arrangement with glass-morphic styling and ambient blur glow effects
- **Full-size analytics** — large 2×2 grid of dedicated CPU, Memory, Disk, and Network charts with 7-line tall bar graphs
- **Animated tab transitions** — slide-left / slide-right page transitions between Processes and Performance tabs

### 🎛️ Performance Sidebar
- **Hover-reveal sidebar** — a slim 12px indicator on the left edge that expands to 20rem on hover
- **Mini bar graphs** — real-time sparkline-style graphs for CPU, Memory, Disk, Ethernet, Wi-Fi, and GPUs
- **Per-adapter network stats** — separate Ethernet and Wi-Fi send/receive rates with auto-detected adapter names
- **GPU monitoring** — NVIDIA GPU utilization and temperature via `nvidia-smi`, with Intel/AMD adapter name detection via WMIC
- **CPU name detection** — reads the processor name from Windows Registry, PowerShell, or WMIC fallback

### ⚠️ High Usage Alerts
- **Anomaly detection popups** — auto-appearing glass-card alerts in the bottom-left corner when CPU, Memory, or GPU usage exceeds configurable thresholds (default: 90%)
- **Per-process alerts** — flags the highest-usage process when any single process exceeds 80% CPU or memory
- **Critical system process protection** — excludes `System`, `csrss`, `svchost`, etc. from high-usage alerts
- **Cooldown throttling** — prevents alert spam with a 15-second per-key cooldown
- **Dismissable with persistence** — "Don't show again" checkbox backed by `localStorage`
- **Auto-dismiss** — alerts disappear after 6 seconds if not manually closed

### 📸 System Snapshot
- **One-click export** — captures a complete freeze-frame of CPU, RAM, Disk, Network, and every running process
- **JSON download** — timestamped file with hostname, platform info, performance metrics, and full process list
- **Floating status bar** — expandable bottom-right pill that reveals live CPU, Memory, and Uptime at a glance

### 🎨 Theming
- **Light / Dark mode** — toggle via the navbar icon, applied instantly with CSS custom properties
- **"Ethereal Lens" design language** — deep navy dark mode (`#0d0b18`) with lavender/violet accents, clean neutral light mode (`#f0f2f5`)
- **Ambient background effects** — decorative gradient blobs with blur that shift between themes
- **Glass-card effects** — backdrop blur, luminous edge borders, subtle hover animations, and depth shadows
- **Material Design icons** — Google Material Symbols Outlined throughout
- **Custom modal system** — unified modal for Run Task and End Task with backdrop blur, spring animation, and context-aware styling (danger mode for critical processes)
- **Toast notifications** — success/error feedback with entrance animations and auto-dismiss
- **Light mode defaults** — app starts in light mode, persists user preference

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
    │   ├── datastore.py        # Thread-safe shared state with rolling deques
    │   └── gpu.py              # GPU detection (nvidia-smi, WMIC, PowerShell)
    └── static/
        ├── index.html          # Dashboard UI (Tailwind CSS + custom CSS vars)
        ├── app.js              # Legacy WebSocket client (kept for reference)
        ├── live.js             # Primary runtime — WebSocket, rendering, modals, alerts
        ├── style.css           # Custom CSS — animations, dark mode overrides
        └── theme.js            # Dynamic CSS variable injection (light/dark palettes)
```

### Data Flow

```
┌──────────────┐    psutil     ┌──────────────┐   Thread Lock   ┌──────────────┐
│  StatsPoller │──────────────▸│   DataStore  │◂──────────────▸│ProcessPoller │
│  (1s loop)   │   CPU/RAM/    │  (deques +   │                │ (child proc) │
│  + GPU poll  │   Disk/Net    │   snapshots)  │  process list  │  2s interval │
│  + NIC stats │   GPU/NIC     │   + per-NIC   │  + grouping    │              │
└──────────────┘               └──────┬───────┘                └──────────────┘
                                      │
                               WebSocket /ws
                               (JSON, 1s push)
                                      │
                                      ▼
                               ┌──────────────┐
                               │   Browser    │
                               │  (live.js)   │
                               │  Bar graphs  │
                               │  Sidebar     │
                               │  Alerts      │
                               │  Process tbl │
                               └──────────────┘
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serve the dashboard UI |
| `WS` | `/ws` | Stream live metrics (CPU, RAM, Disk, Net, GPU, per-NIC, processes, history arrays) |
| `POST` | `/api/run-task` | Launch a new process (`{"command": "notepad"}`) — supports aliases, Start Menu shortcuts, UWP apps |
| `POST` | `/api/end-task` | Terminate processes by PID list (`{"pids": [1234], "name": "..."}`) |
| `GET` | `/api/snapshot` | Download a JSON freeze-frame of the full system state |

### WebSocket Payload

Each WebSocket frame includes:

| Field | Type | Description |
|-------|------|-------------|
| `cpu_percent` | `float` | Overall CPU usage % |
| `ram_used` / `ram_total` / `ram_percent` | `float` | Memory metrics in GB / % |
| `disk_read_rate` / `disk_write_rate` | `float` | Disk throughput in MB/s |
| `net_sent_rate` / `net_recv_rate` | `float` | Network throughput in KB/s |
| `eth_sent_rate` / `eth_recv_rate` | `float` | Ethernet adapter KB/s |
| `wifi_sent_rate` / `wifi_recv_rate` | `float` | Wi-Fi adapter KB/s |
| `eth_adapter_name` / `wifi_adapter_name` | `string` | Auto-detected NIC names |
| `cpu_name` | `string` | Full processor name from registry |
| `gpus` | `array` | GPU objects: `{index, name, util, temp_c}` |
| `cpu_history` / `ram_history` / `disk_history` | `array` | Rolling 60-point history |
| `net_sent_history` / `net_recv_history` | `array` | Rolling 60-point network history |
| `eth_total_history` / `wifi_total_history` | `array` | Per-adapter rolling history |
| `boot_time` | `float` | System boot timestamp (epoch) |
| `processes` | `array` | Grouped process list with `{name, pid, pids, cpu, memory, status, category, threads}` |

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Windows OS** (uses `ctypes.windll` for window enumeration, `winreg` for CPU detection)

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

### Optional (auto-detected)
| Tool | Purpose |
|------|---------|
| `nvidia-smi` | NVIDIA GPU utilization and temperature telemetry |
| `wmic` / `PowerShell` | GPU adapter name detection (Intel/AMD fallback) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, FastAPI, uvicorn |
| **System Metrics** | psutil, ctypes (Win32 API), winreg (CPU name) |
| **GPU Telemetry** | nvidia-smi (NVIDIA), WMIC/PowerShell (adapter names) |
| **Data Transport** | WebSocket (1s push interval) |
| **Frontend** | HTML5, Vanilla JavaScript |
| **Styling** | Tailwind CSS (CDN), Custom CSS variables, Glassmorphism |
| **Fonts** | Manrope (headlines), Inter (body/labels) |
| **Icons** | Google Material Symbols Outlined |
| **Concurrency** | threading + multiprocessing (process poller runs in child process) |

---

## 📝 License

This project is licensed under the MIT License.
