from __future__ import annotations

import subprocess
import platform
from typing import Any


def _parse_nvidia_smi_csv(text: str) -> list[dict[str, Any]]:
    """
    Parses output of:
      nvidia-smi --query-gpu=index,name,utilization.gpu,temperature.gpu --format=csv,noheader,nounits
    """
    gpus: list[dict[str, Any]] = []
    for line in (text or "").splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4:
            continue
        try:
            idx = int(parts[0])
        except Exception:
            continue
        name = parts[1]
        try:
            util = float(parts[2])
        except Exception:
            util = None
        try:
            temp = float(parts[3])
        except Exception:
            temp = None
        gpus.append({"index": idx, "name": name, "util": util, "temp_c": temp})
    return gpus


def _get_video_controller_names() -> list[str]:
    """
    Best-effort adapter name list via WMIC (Windows).
    Returns names in the order WMIC reports them.
    """
    try:
        out = subprocess.check_output(
            ["wmic", "path", "Win32_VideoController", "get", "Name"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.75,
        )
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        # first line is header "Name"
        names = [l for l in lines[1:] if l and l.lower() != "name"]
        if names:
            return names
    except Exception:
        pass
    try:
        out = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name) -join \"`n\"",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=1.0,
        )
        names = [l.strip() for l in out.splitlines() if l.strip()]
        return names
    except Exception:
        return []


def get_gpus() -> list[dict[str, Any]]:
    """
    Best-effort GPU detection for Windows machines.
    - NVIDIA: uses nvidia-smi if present.
    Returns [] if no GPU telemetry is available.
    """
    # Start with adapter names (so Intel/AMD at least show up)
    names = _get_video_controller_names()
    base: list[dict[str, Any]] = [{"index": i, "name": n, "util": None, "temp_c": None} for i, n in enumerate(names)]

    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,name,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.5,
        )
        nvidia = _parse_nvidia_smi_csv(out)
        if nvidia:
            # merge NVIDIA telemetry into base list if possible
            if base:
                for nv in nvidia:
                    nv_name = (nv.get("name") or "").lower()
                    matched = False
                    for b in base:
                        if nv_name and nv_name in (b.get("name") or "").lower():
                            b["util"] = nv.get("util")
                            b["temp_c"] = nv.get("temp_c")
                            matched = True
                            break
                    if not matched:
                        base.append(nv)
                return base
            return nvidia
    except Exception:
        pass
    # Heuristic: laptops with one visible NVIDIA adapter often still have Intel iGPU.
    if len(base) == 1:
        cpu_name = (platform.processor() or "").lower()
        if "intel" in cpu_name:
            base.append({"index": 1, "name": "Intel Integrated Graphics", "util": None, "temp_c": None})
    return base

