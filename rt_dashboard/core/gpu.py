from __future__ import annotations

import re
import subprocess
import platform
import time
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


# ─── Adapter name cache ──────────────────────────────────────────────────
# Adapter names never change at runtime, so we avoid shelling out to WMIC /
# PowerShell on every 1s poll. Refresh occasionally in case a (rare) display
# adapter is hot-added.
_NAMES_TTL = 30.0
_names_cache: list[str] | None = None
_names_ts: float = 0.0


def _video_controller_names_cached() -> list[str]:
    global _names_cache, _names_ts
    now = time.monotonic()
    if _names_cache is None or now - _names_ts >= _NAMES_TTL:
        names = _get_video_controller_names()
        if names or _names_cache is None:
            _names_cache = names
            _names_ts = now
    return _names_cache or []


# ─── Intel / AMD utilization via Windows perf counters ───────────────────
# nvidia-smi only reports NVIDIA GPUs. For Intel/AMD adapters we read the
# Windows "GPU Engine" performance counters (the same source Task Manager
# uses). This spawns a PowerShell process, so the result is throttled and
# cached to keep the per-second stats loop cheap.
_PERF_TTL = 2.5
_perf_cache: dict[int, float] = {}
_perf_ts: float = 0.0


def _query_gpu_engine_util() -> dict[int, float]:
    """
    Returns {physical_gpu_index: utilization_percent} from the
    '\\GPU Engine(*)\\Utilization Percentage' performance counters.

    Instance names look like:
      pid_1234_luid_0x00000000_0x0000abcd_phys_0_eng_0_engtype_3D
    We aggregate per (physical GPU, engine type) and take the busiest engine
    as that GPU's utilization, mirroring Task Manager's headline number.
    """
    try:
        out = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-Counter '\\GPU Engine(*)\\Utilization Percentage' "
                "-ErrorAction SilentlyContinue).CounterSamples "
                "| ForEach-Object { \"$($_.InstanceName)=$($_.CookedValue)\" }",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.5,
        )
    except Exception:
        return {}

    agg: dict[tuple[int, str], float] = {}
    for line in out.splitlines():
        line = line.strip()
        if "=" not in line:
            continue
        inst, _, val = line.rpartition("=")
        try:
            v = float(val)
        except ValueError:
            continue
        if v <= 0.0:
            continue
        m_phys = re.search(r"phys_(\d+)", inst)
        if not m_phys:
            continue
        phys = int(m_phys.group(1))
        m_eng = re.search(r"engtype_([A-Za-z0-9]+)", inst)
        eng = m_eng.group(1).lower() if m_eng else "other"
        key = (phys, eng)
        agg[key] = agg.get(key, 0.0) + v

    result: dict[int, float] = {}
    for (phys, _eng), total in agg.items():
        result[phys] = max(result.get(phys, 0.0), min(100.0, total))
    return result


def _gpu_engine_util_by_phys() -> dict[int, float]:
    global _perf_cache, _perf_ts
    now = time.monotonic()
    if now - _perf_ts < _PERF_TTL:
        return _perf_cache
    _perf_ts = now
    _perf_cache = _query_gpu_engine_util()
    return _perf_cache


def get_gpus() -> list[dict[str, Any]]:
    """
    Best-effort GPU detection for Windows machines.
    - Adapter names: WMIC / PowerShell (cached).
    - NVIDIA util/temp: nvidia-smi (live).
    - Intel/AMD util: Windows GPU Engine perf counters (throttled).
    Returns one entry per physically present adapter, [] if none detected.
    """
    names = _video_controller_names_cached()
    base: list[dict[str, Any]] = [
        {"index": i, "name": n, "util": None, "temp_c": None}
        for i, n in enumerate(names)
    ]

    # NVIDIA telemetry (fast — query live every call).
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
            if base:
                # merge NVIDIA telemetry into the named adapter list
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
            else:
                base = nvidia
    except Exception:
        pass

    # Fill utilization for adapters without NVIDIA telemetry (Intel/AMD) using
    # the GPU Engine perf counters. The perf counters expose no adapter name,
    # and their "physical GPU" index ordering does NOT match WMIC's adapter
    # ordering, so we can't map by index. Instead we hand the still-missing
    # adapters the available counter values in physical-index order — the
    # integrated GPU is virtually always physical index 0, which is the one
    # that needs filling here (NVIDIA dGPUs are already covered by nvidia-smi).
    missing = [g for g in base if g.get("util") is None]
    if missing:
        phys_util = _gpu_engine_util_by_phys()
        if phys_util:
            values = [phys_util[p] for p in sorted(phys_util)]
            for g, v in zip(missing, values):
                g["util"] = round(v, 1)

    return base
