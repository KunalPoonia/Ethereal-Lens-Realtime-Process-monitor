(() => {
  let cachedState = null;
  let appsCollapsed = false;
  let bgCollapsed = false;
  let selectedProcessPid = null;
  let activeModalType = null;
  let processFilterMode = "all";
  let endingCriticalSystemProcess = false;
  let lastHighUsageAlertAt = 0;
  let lastHighUsageAlertKey = "";
  const alertCooldownByKey = new Map();
  const suppressedAlertKeys = new Set();

  const PROCESS_CPU_ALERT_THRESHOLD = 20;
  const PROCESS_MEM_ALERT_THRESHOLD = 80;
  const OVERALL_CPU_ALERT_THRESHOLD = 90;
  const OVERALL_MEM_ALERT_THRESHOLD = 90;
  const OVERALL_GPU_ALERT_THRESHOLD = 90;
  const ALERT_AUTO_DISMISS_MS = 10000;

  const metricHistory = { cpu: [], mem: [], disk: [], net: [], gpu0: [], gpu1: [] };
  const HISTORY_MAX = 20;

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function formatUptime(bootTime) {
    if (!bootTime) return "--:--";
    const uptimeSec = Math.floor(Date.now() / 1000 - bootTime);
    const days = Math.floor(uptimeSec / 86400);
    const hrs = Math.floor((uptimeSec % 86400) / 3600);
    const mins = Math.floor((uptimeSec % 3600) / 60);
    const base = `${String(hrs).padStart(2, "0")}:${String(mins).padStart(2, "0")}`;
    return days > 0 ? `${days}d ${base}` : base;
  }

  function updateSummary(state) {
    setText("sum-cpu", `${Math.round(state.cpu_percent)}%`);
    setText("sum-mem", `${Math.round(state.ram_percent)}%`);
    setText("perf-uptime", formatUptime(state.boot_time));
  }

  function renderBarGraph(selector, history, colorVar) {
    const containers = document.querySelectorAll(selector);
    containers.forEach((container) => {
      if (container.children.length !== history.length) {
        container.innerHTML = history
          .map(() => '<div class="w-full rounded-t-sm transition-all duration-500 ease-out"></div>')
          .join("");
      }
      const bars = container.children;
      for (let i = 0; i < history.length; i += 1) {
        const pct = Math.max(1, Math.min(100, history[i] || 0));
        const age = i / Math.max(1, history.length - 1);
        const opacity = age < 0.33 ? 0.2 : age < 0.66 ? 0.45 : 0.8;
        bars[i].style.height = `${pct}%`;
        bars[i].style.opacity = `${opacity}`;
        bars[i].style.backgroundColor = `var(${colorVar})`;
      }
    });
  }

  function updateTopCards(state) {
    const diskTotal = Math.max(0, state.disk_read_rate + state.disk_write_rate);
    const netTotal = Math.max(0, state.net_sent_rate + state.net_recv_rate);

    document.querySelectorAll(".text-metric-cpu").forEach((icon) => {
      const card = icon.closest(".glass-card");
      if (!card) return;
      const value = card.querySelector(".font-headline");
      const desc = card.querySelector(".font-body");
      if (value) value.innerHTML = `${Math.round(state.cpu_percent)}<span class="text-xl text-[var(--theme-text-muted)] ml-1">%</span>`;
      if (desc) desc.textContent = "Active processing load";
    });

    document.querySelectorAll(".text-metric-mem").forEach((icon) => {
      const card = icon.closest(".glass-card");
      if (!card) return;
      const value = card.querySelector(".font-headline");
      const desc = card.querySelector(".font-body");
      if (value) value.innerHTML = `${state.ram_used.toFixed(1)}<span class="text-xl text-[var(--theme-text-muted)] ml-1">&nbsp;GB</span>`;
      if (desc) desc.textContent = `${Math.round(state.ram_percent)}% of total capacity`;
    });

    document.querySelectorAll(".text-metric-disk").forEach((icon) => {
      const card = icon.closest(".glass-card");
      if (!card) return;
      const value = card.querySelector(".font-headline");
      const desc = card.querySelector(".font-body");
      if (value) value.innerHTML = `${diskTotal.toFixed(1)}<span class="text-xl text-[var(--theme-text-muted)] ml-1">&nbsp;MB/s</span>`;
      if (desc) desc.textContent = `R: ${state.disk_read_rate.toFixed(1)} MB/s  W: ${state.disk_write_rate.toFixed(1)} MB/s`;
    });

    document.querySelectorAll(".text-metric-net").forEach((icon) => {
      const card = icon.closest(".glass-card");
      if (!card) return;
      const value = card.querySelector(".font-headline");
      const desc = card.querySelector(".font-body");
      if (value) value.innerHTML = `${Math.round(netTotal)}<span class="text-xl text-[var(--theme-text-muted)] ml-1">&nbsp;KB/s</span>`;
      if (desc) desc.textContent = `↑ ${state.net_sent_rate.toFixed(1)} KB/s  ↓ ${state.net_recv_rate.toFixed(1)} KB/s`;
    });
  }

  function updatePerformanceCards(state) {
    const diskTotal = Math.max(0, state.disk_read_rate + state.disk_write_rate);
    const netTotal = Math.max(0, state.net_sent_rate + state.net_recv_rate);
    const max = (arr) => (arr.length ? Math.max(...arr) : 0);
    const avg = (arr) => (arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0);

    setText("perf-cpu-val", state.cpu_percent.toFixed(1));
    setText("perf-cpu-peak", `${max(metricHistory.cpu).toFixed(1)}%`);
    setText("perf-cpu-avg", `${avg(metricHistory.cpu).toFixed(1)}%`);

    setText("perf-mem-val", state.ram_used.toFixed(1));
    setText("perf-mem-peak", `${max(metricHistory.mem).toFixed(1)} GB`);
    setText("perf-mem-avg", `${avg(metricHistory.mem).toFixed(1)} GB`);

    setText("perf-disk-val", `${diskTotal.toFixed(0)}`);
    setText("perf-disk-write", `${state.disk_write_rate.toFixed(1)} MB/s`);
    setText("perf-disk-read", `${state.disk_read_rate.toFixed(1)} MB/s`);

    setText("perf-net-val", `${Math.round(netTotal)}`);
    setText("perf-net-down", `${state.net_recv_rate.toFixed(1)} KB/s`);
    setText("perf-net-up", `${state.net_sent_rate.toFixed(1)} KB/s`);
  }

  function updatePerformanceSidebar(state) {
    // Values
    const diskTotal = Math.max(0, state.disk_read_rate + state.disk_write_rate);
    const ethSend = Math.max(0, Number(state.eth_sent_rate || 0));
    const ethRecv = Math.max(0, Number(state.eth_recv_rate || 0));
    const wifiSend = Math.max(0, Number(state.wifi_sent_rate || 0));
    const wifiRecv = Math.max(0, Number(state.wifi_recv_rate || 0));

    setText("sb-cpu-name", state.cpu_name || "CPU");
    setText("sb-cpu-val", `${state.cpu_percent.toFixed(0)}%`);
    setText("sb-mem-val", `${state.ram_used.toFixed(1)}/${state.ram_total.toFixed(1)} GB (${Math.round(state.ram_percent)}%)`);
    setText("sb-disk-val", `${diskTotal.toFixed(1)} MB/s`);
    setText("sb-eth-name", state.eth_adapter_name || "Ethernet");
    setText("sb-wifi-name", state.wifi_adapter_name || "Wi-Fi");
    setText("sb-net-val", `S ${ethSend.toFixed(1)}  R ${ethRecv.toFixed(1)} Kbps`);
    setText("sb-wifi-val", `S ${wifiSend.toFixed(1)}  R ${wifiRecv.toFixed(1)} Kbps`);
    const gpus = Array.isArray(state.gpus) ? state.gpus : [];
    const fmtGpu = (g) => {
      if (!g) return "N/A";
      const util = g.util === null || g.util === undefined ? "N/A" : `${Math.round(g.util)}%`;
      const temp = g.temp_c === null || g.temp_c === undefined ? "" : ` (${Math.round(g.temp_c)}°C)`;
      return util === "N/A" ? "N/A" : `${util}${temp}`;
    };
    const gpuName = (g, fallback) => (g?.name ? String(g.name) : fallback);
    setText("sb-gpu0-name", gpuName(gpus[0], "GPU 0"));
    setText("sb-gpu1-name", gpuName(gpus[1], "GPU 1"));
    setText("sb-gpu0-val", fmtGpu(gpus[0]));
    setText("sb-gpu1-val", fmtGpu(gpus[1]));

    // Mini graphs (use last 14 points)
    const tail = (arr, n) => (Array.isArray(arr) ? arr.slice(-n) : []);
    const cpu = tail(state.cpu_history, 14);
    const mem = tail(state.ram_history, 14); // already percent
    const disk = tail(state.disk_history, 14).map((v) => Math.min(100, (Number(v || 0) / 500) * 100));
    const netCombined = tail(state.net_sent_history, 14).map((v, i) => {
      const recv = state.net_recv_history?.[state.net_recv_history.length - 14 + i] || 0;
      return Math.min(100, ((Number(v || 0) + Number(recv || 0)) / 10000) * 100);
    });
    const ethRaw = tail(state.eth_total_history, 14).map((v) => Number(v || 0));
    const wifiRaw = tail(state.wifi_total_history, 14).map((v) => Number(v || 0));
    const toPctDynamic = (vals) => {
      const peak = Math.max(1, ...vals);
      return vals.map((v) => Math.min(100, (v / peak) * 100));
    };
    const eth = toPctDynamic(ethRaw);
    const wifi = toPctDynamic(wifiRaw);
    const ensurePoints = (arr, count = 14) => {
      const src = Array.isArray(arr) ? arr.slice(-count) : [];
      if (src.length >= count) return src;
      const fill = src.length ? src[0] : 0;
      return new Array(count - src.length).fill(fill).concat(src);
    };
    const gpu0Current = Number(gpus[0]?.util);
    const gpu1Current = Number(gpus[1]?.util);
    const gpu0 = Number.isFinite(gpu0Current) ? ensurePoints(metricHistory.gpu0, 14) : [];
    const gpu1 = Number.isFinite(gpu1Current) ? ensurePoints(metricHistory.gpu1, 14) : [];

    renderBarGraph(".perf-sb-graph-cpu", cpu, "--theme-primary-text");
    renderBarGraph(".perf-sb-graph-mem", mem, "--theme-secondary-dim-text");
    renderBarGraph(".perf-sb-graph-disk", disk, "--theme-tertiary-text");
    renderBarGraph(".perf-sb-graph-net", eth.length ? eth : netCombined, "--theme-secondary-text");
    renderBarGraph(".perf-sb-graph-wifi", wifi.length ? wifi : netCombined, "--theme-secondary-text");
    renderBarGraph(".perf-sb-graph-gpu0", gpu0, "--theme-secondary-text");
    renderBarGraph(".perf-sb-graph-gpu1", gpu1, "--theme-secondary-text");
  }

  function getStatusBadge(proc, state) {
    const cpuPct = Number(proc.cpu || 0);
    const totalRamMb = Math.max(1, Number(state.ram_total || 0) * 1024);
    const memPct = (Number(proc.memory || 0) / totalRamMb) * 100;

    // Critical: 71-100
    if (cpuPct >= 71 || memPct >= 71) {
      return '<span class="px-2.5 py-1 rounded-md text-[11px] font-bold font-label uppercase tracking-[0.16em] bg-[var(--theme-error-bg)] text-[var(--theme-error-text)] border-2 border-[var(--theme-error-border)] shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] status-critical">Critical</span>';
    }
    // Warning: 41-70
    if (cpuPct >= 41 || memPct >= 41) {
      return '<span class="px-2.5 py-1 rounded-md text-[11px] font-bold font-label uppercase tracking-[0.16em] bg-[var(--theme-secondary-bg)] text-[var(--theme-secondary-text)] border-2 border-[var(--theme-secondary-border)] shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] status-warning">Warning</span>';
    }
    // Stable: 0-40
    return '<span class="px-2.5 py-1 rounded-md text-[11px] font-bold font-label uppercase tracking-[0.16em] bg-[var(--theme-tertiary-bg)] text-[var(--theme-tertiary-text)] border-2 border-[var(--theme-tertiary-border)] shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]">Stable</span>';
  }

  function isCriticalSystemProcess(proc) {
    if (!proc) return false;
    const criticalNames = new Set([
      "system",
      "registry",
      "smss",
      "csrss",
      "wininit",
      "winlogon",
      "services",
      "lsass",
      "svchost",
    ]);
    const lowered = (proc.name || "").toLowerCase();
    return Number(proc.pid) <= 4 || criticalNames.has(lowered);
  }

  function dismissHighUsageAlert(wrap) {
    if (!wrap || !wrap.isConnected) return;
    if (wrap.dataset.dismissing === "1") return;
    wrap.dataset.dismissing = "1";

    const existingTimer = Number(wrap.dataset.timeoutId || 0);
    if (existingTimer) {
      window.clearTimeout(existingTimer);
      delete wrap.dataset.timeoutId;
    }

    wrap.classList.add("high-usage-alert-exit");
    window.setTimeout(() => {
      if (wrap.isConnected) wrap.remove();
    }, 320);
  }

  function scheduleHighUsageAlertDismiss(wrap) {
    if (!wrap) return;
    const existingTimer = Number(wrap.dataset.timeoutId || 0);
    if (existingTimer) {
      window.clearTimeout(existingTimer);
    }
    const timeoutId = window.setTimeout(() => {
      dismissHighUsageAlert(wrap);
    }, ALERT_AUTO_DISMISS_MS);
    wrap.dataset.timeoutId = String(timeoutId);
  }

  function showHighUsageAlert(key, title, message, suppressKey = key) {
    const stack = document.getElementById("high-usage-alert-stack");
    if (!stack) return;
    if (suppressedAlertKeys.has(suppressKey)) return;

    const existing = stack.querySelector(`[data-alert-key="${key}"]`);
    if (existing) {
      const titleEl = existing.querySelector(".high-usage-alert-title");
      const textEl = existing.querySelector(".high-usage-alert-text");
      const checkboxEl = existing.querySelector(".high-usage-alert-dismiss");
      existing.dataset.suppressKey = suppressKey;
      if (titleEl) titleEl.textContent = title;
      if (textEl) textEl.textContent = message;
      if (checkboxEl) checkboxEl.checked = suppressedAlertKeys.has(suppressKey);
      existing.dataset.dismissing = "0";
      existing.classList.remove("high-usage-alert-exit");
      scheduleHighUsageAlertDismiss(existing);
      return;
    }

    const wrap = document.createElement("div");
    wrap.className = "glass-card high-usage-alert rounded-2xl p-4 luminous-edge border border-[var(--theme-border-strong)] shadow-2xl shadow-black/30 pointer-events-auto";
    wrap.setAttribute("data-alert-key", key);
    wrap.dataset.dismissing = "0";
    wrap.dataset.suppressKey = suppressKey;
    wrap.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div class="flex flex-col gap-0.5">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-[var(--theme-error-text)] text-[20px]">warning</span>
            <h4 class="high-usage-alert-title font-headline font-bold text-[var(--theme-text-strong)] text-sm tracking-tight">${title}</h4>
          </div>
          <p class="high-usage-alert-text text-xs text-[var(--theme-text-muted)] leading-snug">${message}</p>
        </div>
        <button class="high-usage-alert-close w-8 h-8 flex items-center justify-center rounded-full hover:bg-[var(--theme-hover)] text-[var(--theme-text-muted)] transition-colors" title="Close">
          <span class="material-symbols-outlined text-lg">close</span>
        </button>
      </div>
      <label class="mt-3 flex items-center gap-2 text-xs text-[var(--theme-text-muted)] select-none cursor-pointer">
        <input type="checkbox" class="high-usage-alert-dismiss rounded border-[var(--theme-border-strong)] bg-[var(--theme-glass)] text-primary" />
        Don't show again
      </label>
    `;

    wrap.querySelector(".high-usage-alert-close")?.addEventListener("click", () => dismissHighUsageAlert(wrap));
    wrap.querySelector(".high-usage-alert-dismiss")?.addEventListener("change", (e) => {
      const currentSuppressKey = wrap.dataset.suppressKey || key;
      if (e.target.checked) {
        suppressedAlertKeys.add(currentSuppressKey);
      } else {
        suppressedAlertKeys.delete(currentSuppressKey);
      }
    });

    stack.appendChild(wrap);
    scheduleHighUsageAlertDismiss(wrap);
  }

  function hideHighUsageAlert() {
    const stack = document.getElementById("high-usage-alert-stack");
    if (stack) stack.innerHTML = "";
  }

  function maybeShowHighUsageAlert(state) {
    const now = Date.now();
    const canShow = (key) => {
      const prev = alertCooldownByKey.get(key) || 0;
      if (now - prev < 15000) return false;
      alertCooldownByKey.set(key, now);
      return true;
    };

    const overallCpu = Number(state.cpu_percent || 0);
    const overallMem = Number(state.ram_percent || 0);
    const gpus = Array.isArray(state.gpus) ? state.gpus : [];
    if (overallCpu >= OVERALL_CPU_ALERT_THRESHOLD && canShow("overall-cpu")) {
      showHighUsageAlert("overall-cpu", "CPU anomaly detected", `Overall CPU usage is ${overallCpu.toFixed(1)}%.`, "overall-cpu");
    }
    if (overallMem >= OVERALL_MEM_ALERT_THRESHOLD && canShow("overall-mem")) {
      showHighUsageAlert("overall-mem", "Memory anomaly detected", `Overall memory usage is ${overallMem.toFixed(1)}%.`, "overall-mem");
    }
    for (let i = 0; i < gpus.length; i += 1) {
      const util = Number(gpus[i]?.util);
      if (!Number.isFinite(util)) continue;
      if (util >= OVERALL_GPU_ALERT_THRESHOLD) {
        const name = String(gpus[i]?.name || `GPU ${i}`).trim();
        const gpuKey = `overall-gpu-${i}`;
        if (canShow(gpuKey)) {
          showHighUsageAlert(gpuKey, "GPU anomaly detected", `${name} usage is ${util.toFixed(1)}%.`, gpuKey);
        }
      }
    }

    const procs = Array.isArray(state.processes) ? state.processes : [];
    const totalRamMb = Math.max(1, Number(state.ram_total || 0) * 1024);

    let best = null;
    for (const p of procs) {
      if (!p) continue;
      if (isCriticalSystemProcess(p)) continue; // exclude System processes

      const cpuPct = Number(p.cpu || 0);
      const memPct = (Number(p.memory || 0) / totalRamMb) * 100;
      const score = Math.max(
        cpuPct >= PROCESS_CPU_ALERT_THRESHOLD ? cpuPct : 0,
        memPct >= PROCESS_MEM_ALERT_THRESHOLD ? memPct : 0
      );
      if (score <= 0) continue;

      if (!best || score > best.score) {
        best = { proc: p, cpuPct, memPct, score };
      }
    }

    if (!best) return;

    const key = `${best.proc.pid}:${Math.round(best.cpuPct)}:${Math.round(best.memPct)}`;
    // throttle: don't spam the same alert repeatedly
    if (key === lastHighUsageAlertKey && now - lastHighUsageAlertAt < 15000) return;

    lastHighUsageAlertKey = key;
    lastHighUsageAlertAt = now;

    const parts = [];
    if (best.cpuPct >= PROCESS_CPU_ALERT_THRESHOLD) parts.push(`CPU ${best.cpuPct.toFixed(1)}%`);
    if (best.memPct >= PROCESS_MEM_ALERT_THRESHOLD) parts.push(`Memory ${best.memPct.toFixed(1)}%`);
    showHighUsageAlert(
      "process-high-usage",
      "High usage detected",
      `${best.proc.name} (PID ${best.proc.pid}) is high: ${parts.join(" · ")}`,
      `process:${best.proc.pid}`
    );
  }

  function getProcessIcon(procName, isApp) {
    const lowered = (procName || "").toLowerCase();
    if (!isApp) {
      return {
        icon: "settings_system_daydream",
        iconClass: "bg-[var(--theme-outline-bg)] text-[var(--theme-text-muted)] border border-[var(--theme-outline-border)]",
      };
    }
    if (lowered.includes("brave") || lowered.includes("chrome") || lowered.includes("edge") || lowered.includes("firefox")) {
      return {
        icon: "language",
        iconClass: "bg-orange-500/20 text-orange-400 border border-orange-500/30",
      };
    }
    if (lowered.includes("spotify") || lowered.includes("music")) {
      return {
        icon: "music_note",
        iconClass: "bg-green-500/20 text-green-400 border border-green-500/30",
      };
    }
    if (lowered.includes("python") || lowered.includes("code")) {
      return {
        icon: "terminal",
        iconClass: "bg-blue-500/20 text-blue-400 border border-blue-500/30",
      };
    }
    return {
      icon: "apps",
      iconClass: "bg-primary-fixed-dim/20 text-primary-fixed-dim border border-primary-fixed-dim/30",
    };
  }

  function buildProcessRow(proc, state, isApp) {
    const memText = proc.memory >= 1024 ? `${(proc.memory / 1024).toFixed(1)} GB` : `${proc.memory.toFixed(1)} MB`;
    const { icon, iconClass } = getProcessIcon(proc.name, isApp);
    const isSelected = selectedProcessPid === proc.pid;
    return `<tr onclick="window.selectProcess(${proc.pid})" class="${isSelected ? "process-row-selected bg-white/10" : ""} hover:bg-[var(--theme-hover)] transition-colors group cursor-pointer">
      <td class="px-6 py-4 text-[var(--theme-text-muted)] font-mono"><span class="pid-cell">${proc.pid}</span></td>
      <td class="px-6 py-4 font-semibold">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 shrink-0 rounded flex items-center justify-center ${iconClass}">
            <span class="material-symbols-outlined text-sm">${icon}</span>
          </div>
          <span class="truncate">${proc.name}</span>
        </div>
      </td>
      <td class="px-6 py-4">${getStatusBadge(proc, state)}</td>
      <td class="px-6 py-4 text-metric-unified font-mono font-medium">${proc.cpu.toFixed(1)}%</td>
      <td class="px-6 py-4 text-metric-unified font-mono font-medium">${memText}</td>
      <td class="px-6 py-4 text-metric-unified font-mono font-medium">${(state.disk_total_rate || 0).toFixed(1)} MB/s</td>
      <td class="px-6 py-4 text-metric-unified font-mono font-medium">${(state.net_recv_rate + state.net_sent_rate).toFixed(1)} KB/s</td>
    </tr>`;
  }

  function buildSectionHeader(label, count, collapsed, key) {
    const rotationClass = collapsed ? "-rotate-90" : "";
    return `<tr class="bg-[var(--theme-glass)] cursor-pointer select-none hover:bg-[var(--theme-hover)] transition-colors" onclick="window.toggleProcessGroup('${key}')">
      <td colspan="7" class="px-6 py-2.5 text-xs font-bold text-[var(--theme-text-muted)] border-y border-[var(--theme-border)]">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-sm transition-transform duration-200 ${rotationClass}">expand_more</span>
          ${label} (${count})
        </div>
      </td>
    </tr>`;
  }

  function renderProcesses(state) {
    const body = document.getElementById("process-list");
    if (!body) return;

    const filter = (document.getElementById("search-input")?.value || "").trim().toLowerCase();
    const processes = (state.processes || [])
      .filter((p) => !filter || `${p.name} ${p.pid}`.toLowerCase().includes(filter))
      .filter((p) => {
        const cpuPct = Number(p.cpu || 0);
        const totalRamMb = Math.max(1, Number(state.ram_total || 0) * 1024);
        const memPct = (Number(p.memory || 0) / totalRamMb) * 100;
        const lowered = (p.name || "").toLowerCase();
        if (processFilterMode === "active") return cpuPct >= 1 || memPct >= 1;
        if (processFilterMode === "high") return cpuPct >= 50 || memPct >= 50;
        if (processFilterMode === "system") {
          return lowered.includes("system") || lowered.includes("service") || lowered.includes("host") || lowered.includes("svchost") || p.pid <= 4;
        }
        return true;
      })
      .sort((a, b) => b.cpu - a.cpu)
      .slice(0, 100);

    const apps = processes.filter((p) => p.category === "app");
    const background = processes.filter((p) => p.category !== "app");
    const presentPids = new Set(processes.map((p) => p.pid));
    if (selectedProcessPid !== null && !presentPids.has(selectedProcessPid)) {
      selectedProcessPid = null;
    }

    let html = "";
    html += buildSectionHeader("Apps", apps.length, appsCollapsed, "apps");
    if (!appsCollapsed) {
      html += apps.map((proc) => buildProcessRow(proc, state, true)).join("");
    }

    html += buildSectionHeader("Background processes", background.length, bgCollapsed, "bg");
    if (!bgCollapsed) {
      html += background.map((proc) => buildProcessRow(proc, state, false)).join("");
    }

    body.innerHTML = html;
    updateSelectionUI();
  }

  function updateSelectionUI() {
    const endBtn = document.getElementById("btn-end-task");
    if (!endBtn) return;
    if (selectedProcessPid !== null) {
      endBtn.disabled = false;
      endBtn.className = "flex items-center gap-2 px-3 py-1.5 rounded-lg bg-error/20 border border-error/50 backdrop-blur-md text-xs font-semibold text-error transition-all hover:scale-105 shadow-[0_0_15px_rgba(186,26,26,0.4)]";
    } else {
      endBtn.disabled = true;
      endBtn.className = "flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 backdrop-blur-md text-xs font-semibold text-white/40 transition-all cursor-not-allowed";
    }
  }

  async function endSelectedTasks() {
    if (!cachedState || selectedProcessPid === null) return;
    const selected = cachedState.processes.filter((p) => p.pid === selectedProcessPid);
    const pidSet = new Set();
    selected.forEach((proc) => {
      if (Array.isArray(proc.pids) && proc.pids.length) {
        proc.pids.forEach((pid) => pidSet.add(pid));
      } else {
        pidSet.add(proc.pid);
      }
    });

    if (pidSet.size === 0) return;
    try {
      const res = await fetch("/api/end-task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pids: [...pidSet], name: "selected process" }),
      });
      await res.json();
      selectedProcessPid = null;
      endingCriticalSystemProcess = false;
      updateSelectionUI();
    } catch (_err) {
      // noop
    }
  }

  async function runNewTask(command) {
    if (!command || !command.trim()) return;
    try {
      await fetch("/api/run-task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: command.trim() }),
      });
    } catch (_err) {
      // noop
    }
  }

  function closeTaskModal() {
    const overlay = document.getElementById("modal-overlay");
    const wrapper = document.getElementById("main-wrapper");
    if (overlay) overlay.classList.remove("active");
    if (wrapper) wrapper.classList.remove("modal-blur-active");
    document.body.style.overflow = "";
    activeModalType = null;
    endingCriticalSystemProcess = false;
  }

  function openTaskModal(type) {
    const overlay = document.getElementById("modal-overlay");
    const wrapper = document.getElementById("main-wrapper");
    const title = document.getElementById("modal-title");
    const subtitle = document.getElementById("modal-subtitle");
    const icon = document.getElementById("modal-icon");
    const iconWrap = document.getElementById("modal-icon-wrap");
    const commandRow = document.getElementById("modal-command-row");
    const actionBtn = document.getElementById("modal-action-btn");
    const input = document.getElementById("modal-command-input");
    const selectionNote = document.getElementById("modal-selection-note");
    if (!overlay || !wrapper || !title || !subtitle || !icon || !iconWrap || !commandRow || !actionBtn || !input || !selectionNote) return;

    activeModalType = type;
    if (type === "run") {
      title.textContent = "Run New Task";
      subtitle.textContent = "Execute a new system process or command";
      icon.textContent = "terminal";
      iconWrap.className = "w-14 h-14 rounded-full bg-primary-container/20 border border-primary-container/30 flex items-center justify-center text-primary-fixed-dim";
      actionBtn.textContent = "EXECUTE TASK";
      actionBtn.className = "flex-1 px-6 py-3 rounded-xl bg-primary text-[var(--theme-text-strong)] font-bold text-sm shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all hover:-translate-y-0.5 active:translate-y-0 active:scale-95 btn-glow";
      input.value = "";
      input.placeholder = "e.g. notepad or code";
      commandRow.classList.remove("hidden");
      selectionNote.classList.add("hidden");
      endingCriticalSystemProcess = false;
    } else {
      const selected = cachedState?.processes?.find((p) => p.pid === selectedProcessPid);
      endingCriticalSystemProcess = isCriticalSystemProcess(selected);

      title.textContent = endingCriticalSystemProcess ? "System Failure Alert" : "End System Task";
      subtitle.textContent = endingCriticalSystemProcess
        ? "This is a critical Windows process. Ending it may crash or freeze your system."
        : "Terminate the currently selected process";
      icon.textContent = endingCriticalSystemProcess ? "warning" : "stop_circle";
      iconWrap.className = endingCriticalSystemProcess
        ? "w-14 h-14 rounded-full bg-[var(--theme-error-bg)] border border-[var(--theme-error-border)] flex items-center justify-center text-[var(--theme-error-text)] status-critical"
        : "w-14 h-14 rounded-full bg-[var(--theme-secondary-bg)] border border-[var(--theme-secondary-border)] flex items-center justify-center text-[var(--theme-secondary-text)]";
      actionBtn.textContent = endingCriticalSystemProcess ? "FORCE TERMINATE" : "TERMINATE TASK";
      actionBtn.className = endingCriticalSystemProcess
        ? "flex-1 px-6 py-3 rounded-xl bg-error text-[var(--theme-text-strong)] font-bold text-sm shadow-lg shadow-error/20 hover:shadow-error/40 transition-all hover:-translate-y-0.5 active:translate-y-0 active:scale-95 status-critical"
        : "flex-1 px-6 py-3 rounded-xl bg-error text-[var(--theme-text-strong)] font-bold text-sm shadow-lg shadow-error/20 hover:shadow-error/40 transition-all hover:-translate-y-0.5 active:translate-y-0 active:scale-95";
      commandRow.classList.add("hidden");
      if (!selectedProcessPid) {
        selectionNote.textContent = "";
        selectionNote.classList.add("hidden");
      } else if (endingCriticalSystemProcess) {
        selectionNote.textContent = `CRITICAL: ${selected?.name || "System process"} (PID ${selectedProcessPid}). Continue only if absolutely necessary.`;
        selectionNote.classList.remove("hidden");
      } else {
        selectionNote.textContent = `Selected: ${selected?.name || "Process"} (PID ${selectedProcessPid})`;
        selectionNote.classList.remove("hidden");
      }
    }

    overlay.classList.add("active");
    wrapper.classList.add("modal-blur-active");
    document.body.style.overflow = "hidden";
    if (type === "run") {
      setTimeout(() => input.focus(), 0);
    }
  }

  async function handleModalAction() {
    if (activeModalType === "run") {
      const command = document.getElementById("modal-command-input")?.value || "";
      await runNewTask(command);
      closeTaskModal();
      return;
    }
    if (activeModalType === "end") {
      await endSelectedTasks();
      closeTaskModal();
    }
  }

  async function snapshotSystem() {
    try {
      const res = await fetch("/api/snapshot");
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
      a.href = url;
      a.download = `snapshot_${ts}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (_err) {
      // noop
    }
  }

  function updateAll(state) {
    cachedState = state;
    const diskTotal = Math.max(0, state.disk_read_rate + state.disk_write_rate);
    const netTotal = Math.max(0, state.net_sent_rate + state.net_recv_rate);

    metricHistory.cpu = (state.cpu_history || []).slice(-HISTORY_MAX);
    metricHistory.mem = (state.ram_history || []).map((v) => Math.max(0, Math.min(100, v))).slice(-HISTORY_MAX);
    metricHistory.disk = (state.disk_history || []).map((v) => Math.min(100, (v / 500) * 100)).slice(-HISTORY_MAX);
    metricHistory.net = (state.net_sent_history || []).map((v, i) => {
      const recv = state.net_recv_history?.[i] || 0;
      return Math.min(100, ((v + recv) / 10000) * 100);
    }).slice(-HISTORY_MAX);
    const gpuSamples = Array.isArray(state.gpus) ? state.gpus : [];
    const gpu0 = gpuSamples[0];
    const gpu1 = gpuSamples[1];
    const gpu0Util = Number(gpu0?.util);
    const gpu1Util = Number(gpu1?.util);
    const gpu0Pct = Number.isFinite(gpu0Util) ? Math.max(0, Math.min(100, gpu0Util)) : 0;
    const gpu1Pct = Number.isFinite(gpu1Util) ? Math.max(0, Math.min(100, gpu1Util)) : 0;
    metricHistory.gpu0 = [...metricHistory.gpu0, gpu0Pct].slice(-HISTORY_MAX);
    metricHistory.gpu1 = [...metricHistory.gpu1, gpu1Pct].slice(-HISTORY_MAX);

    if (!metricHistory.cpu.length) {
      metricHistory.cpu = [state.cpu_percent];
      metricHistory.mem = [state.ram_percent];
      metricHistory.disk = [Math.min(100, (diskTotal / 500) * 100)];
      metricHistory.net = [Math.min(100, (netTotal / 10000) * 100)];
      metricHistory.gpu0 = [gpu0Pct];
      metricHistory.gpu1 = [gpu1Pct];
    }

    updateSummary(state);
    updateTopCards(state);
    updatePerformanceCards(state);
    updatePerformanceSidebar(state);
    renderBarGraph(".graph-container-cpu", metricHistory.cpu, "--theme-primary-text");
    renderBarGraph(".graph-container-mem", metricHistory.mem, "--theme-secondary-dim-text");
    renderBarGraph(".graph-container-disk", metricHistory.disk, "--theme-tertiary-text");
    renderBarGraph(".graph-container-net", metricHistory.net, "--theme-secondary-text");
    renderProcesses(state);
    maybeShowHighUsageAlert(state);
  }

  function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onmessage = (event) => {
      updateAll(JSON.parse(event.data));
    };

    ws.onclose = () => {
      setTimeout(connectWebSocket, 1500);
    };
  }

  document.addEventListener("DOMContentLoaded", () => {
    window.runNewTask = () => openTaskModal("run");
    window.endSelectedTasks = () => openTaskModal("end");
    window.closeTaskModal = closeTaskModal;
    window.toggleProcessGroup = (key) => {
      if (key === "apps") appsCollapsed = !appsCollapsed;
      if (key === "bg") bgCollapsed = !bgCollapsed;
      if (cachedState) renderProcesses(cachedState);
    };
    window.setProcessFilter = (mode) => {
      processFilterMode = mode;
      document.getElementById("filter-menu")?.classList.add("hidden");
      if (cachedState) renderProcesses(cachedState);
    };
    window.refreshProcessList = () => {
      document.getElementById("more-menu")?.classList.add("hidden");
      if (cachedState) renderProcesses(cachedState);
    };
    window.collapseAllGroups = () => {
      appsCollapsed = true;
      bgCollapsed = true;
      document.getElementById("more-menu")?.classList.add("hidden");
      if (cachedState) renderProcesses(cachedState);
    };
    window.expandAllGroups = () => {
      appsCollapsed = false;
      bgCollapsed = false;
      document.getElementById("more-menu")?.classList.add("hidden");
      if (cachedState) renderProcesses(cachedState);
    };
    window.clearSelectedProcess = () => {
      selectedProcessPid = null;
      document.getElementById("more-menu")?.classList.add("hidden");
      if (cachedState) renderProcesses(cachedState);
    };
    window.selectProcess = (pid) => {
      selectedProcessPid = selectedProcessPid === pid ? null : pid;
      if (cachedState) renderProcesses(cachedState);
    };

    connectWebSocket();
    document.getElementById("search-input")?.addEventListener("input", () => {
      if (cachedState) renderProcesses(cachedState);
    });
    document.getElementById("snapshot-btn")?.addEventListener("click", snapshotSystem);
    document.getElementById("btn-end-task")?.addEventListener("click", () => openTaskModal("end"));
    document.getElementById("btn-run-task")?.addEventListener("click", () => openTaskModal("run"));
    document.getElementById("modal-action-btn")?.addEventListener("click", handleModalAction);
    document.getElementById("modal-command-input")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleModalAction();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeTaskModal();
    });
    // High usage alert wiring is dynamic per stacked popup
    document.addEventListener("click", (e) => {
      const menu = document.getElementById("more-menu");
      const btn = document.getElementById("btn-more");
      const filterMenu = document.getElementById("filter-menu");
      const filterBtn = document.getElementById("btn-filter");
      if (menu && btn && !menu.contains(e.target) && !btn.contains(e.target)) {
        menu.classList.add("hidden");
      }
      if (filterMenu && filterBtn && !filterMenu.contains(e.target) && !filterBtn.contains(e.target)) {
        filterMenu.classList.add("hidden");
      }
    });
    updateSelectionUI();
  });
})();
