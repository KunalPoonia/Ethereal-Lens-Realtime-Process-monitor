# ⚡ Real-Time Process Dashboard

A sleek, native Windows desktop app for real-time system monitoring — built with **PyQt6**, **psutil**, and **pyqtgraph**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 📋 Processes Tab
- **Live process table** — PID, Name, CPU%, Memory, Status, User
- **Sortable columns** — click any header to sort ascending/descending
- **Search & filter** — instantly find processes by name or PID
- **Right-click context menu** — End Task or Set Priority (6 levels)
- **Auto-refresh** every second with scroll position preserved

### 📈 Performance Tab
- **Rolling 60-second graphs** for CPU, RAM, Disk, and Network
- **Filled area curves** with smooth updates
- **Summary stats** under each graph (e.g., `8.2 GB / 16.0 GB used`)
- **Auto-scaling** network Y-axis based on peak traffic
- **Card-style layout** — clean 2×2 grid

### 🎨 Theming
- **Dark / Light mode** toggle button in the toolbar
- Professional QSS styling with hover effects and smooth transitions

---

## 🏗️ Architecture

```
rt_dashboard/
├── main.py                  # Entry point
├── config.py                # Theme colors, poll interval, constants
├── core/
│   ├── poller.py            # QThread — polls psutil every second
│   └── datastore.py         # Thread-safe shared state, rolling deques
└── ui/
    ├── main_window.py       # Root window, tab bar, theme toggle
    ├── processes_tab.py     # Process table, search, right-click menu
    ├── performance_tab.py   # Graph panels (CPU/RAM/Disk/Net)
    └── styles.py            # QSS dark + light theme strings
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Windows OS**

### Installation

```bash
# Clone the repo
git clone https://github.com/KunalPoonia/Real-time-Process-monitor.git
cd Real-time-Process-monitor

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
cd rt_dashboard
python main.py
```

---

## 📦 Dependencies

| Package      | Purpose                          |
|-------------|----------------------------------|
| `PyQt6`      | GUI framework                    |
| `psutil`     | System metrics & process info    |
| `pyqtgraph`  | High-performance live graphs     |
| `numpy`      | Numerical array operations       |

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **GUI Framework:** PyQt6
- **Graphing:** pyqtgraph
- **System Metrics:** psutil
- **Styling:** Custom QSS (Qt Style Sheets)
- **Threading:** QThread for non-blocking polling

---

## 📝 License

This project is licensed under the MIT License.
