let selectedPid = null;
let selectedName = null;
let selectedPids = [];
let cachedState = null;
let currentSort = 'name'; // 'name', 'cpu', 'memory'
let appsCollapsed = false;
let bgCollapsed = false;

function toggleSection(section) {
    if (section === 'apps') appsCollapsed = !appsCollapsed;
    else if (section === 'bg') bgCollapsed = !bgCollapsed;
    renderProcesses();
}

// Connect to the FastAPI WebSocket
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${location.host}/ws`);

ws.onopen = () => {
    console.log('WebSocket connected');
    const statusText = document.getElementById('connection-status');
    if (statusText) {
        statusText.textContent = 'CONNECTED';
        statusText.classList.add('text-primary');
        statusText.classList.remove('text-error', 'text-on-surface-variant');
    }
};

ws.onclose = () => {
    console.log('WebSocket disconnected');
    const statusText = document.getElementById('connection-status');
    if (statusText) {
        statusText.textContent = 'DISCONNECTED';
        statusText.classList.add('text-error');
        statusText.classList.remove('text-primary', 'text-on-surface-variant');
    }
};

ws.onmessage = (event) => {
    cachedState = JSON.parse(event.data);
    updateMetrics(cachedState);
    if (!document.getElementById('view-processes').classList.contains('hidden')) {
        renderProcesses();
    }
};

let cpuPeak = 0;
let prevCpu = 0;

function updateMetrics(state) {
    // Top summary bar in the Processes View
    document.getElementById('sum-cpu').textContent = `${Math.round(state.cpu_percent)}%`;
    document.getElementById('sum-mem').textContent = `${Math.round(state.ram_percent)}%`;

    // -- CPU Card --
    document.getElementById('perf-cpu').textContent = `${state.cpu_percent.toFixed(1)}%`;
    
    // CPU delta (change from previous reading)
    const cpuDelta = state.cpu_percent - prevCpu;
    const deltaEl = document.getElementById('perf-cpu-delta');
    if (deltaEl) {
        const arrow = cpuDelta >= 0 ? 'north_east' : 'south_east';
        deltaEl.innerHTML = `<span class="material-symbols-outlined text-sm">${arrow}</span> ${Math.abs(cpuDelta).toFixed(1)}%`;
    }
    prevCpu = state.cpu_percent;

    // CPU peak
    if (state.cpu_percent > cpuPeak) cpuPeak = state.cpu_percent;
    const peakEl = document.getElementById('perf-cpu-peak');
    if (peakEl) peakEl.textContent = `${cpuPeak.toFixed(1)}%`;
    
    // ── RAM Card ──
    const ramSpan = document.getElementById('perf-mem');
    ramSpan.innerHTML = `${state.ram_used.toFixed(1)} <span class="text-xl font-light text-on-surface-variant">/ ${state.ram_total.toFixed(1)} GB</span>`;
    const memPctEl = document.getElementById('perf-mem-pct');
    if (memPctEl) memPctEl.textContent = `${Math.round(state.ram_percent)}%`;
    
    // ── Disk Card ──
    const diskTotal = state.disk_read_rate + state.disk_write_rate;
    const diskSpan = document.getElementById('perf-disk');
    diskSpan.innerHTML = `${diskTotal.toFixed(1)} <span class="text-xl font-light text-on-surface-variant">MB/s</span>`;
    const diskReadEl = document.getElementById('perf-disk-read');
    if (diskReadEl) diskReadEl.textContent = `${state.disk_read_rate.toFixed(1)} MB/s`;
    const diskWriteEl = document.getElementById('perf-disk-write');
    if (diskWriteEl) diskWriteEl.textContent = `${state.disk_write_rate.toFixed(1)} MB/s`;
    
    // ── Network Card ──
    const netTotal = state.net_sent_rate + state.net_recv_rate;
    const netSpan = document.getElementById('perf-net');
    netSpan.innerHTML = `${Math.round(netTotal)} <span class="text-xl font-light text-on-surface-variant">KB/s</span>`;
    const netRecvEl = document.getElementById('perf-net-recv');
    if (netRecvEl) netRecvEl.textContent = `${state.net_recv_rate.toFixed(1)} KB/s`;
    const netSentEl = document.getElementById('perf-net-sent');
    if (netSentEl) netSentEl.textContent = `${state.net_sent_rate.toFixed(1)} KB/s`;

    // ── Live Bar Graphs ──
    if (state.cpu_history) renderBarGraph('graph-cpu', state.cpu_history, 'primary');
    if (state.ram_history) renderBarGraph('graph-mem', state.ram_history, 'secondary');

    // ── Uptime & Last Sync ──
    if (state.boot_time) {
        const uptimeSec = Math.floor(Date.now() / 1000 - state.boot_time);
        const days = Math.floor(uptimeSec / 86400);
        const hrs  = Math.floor((uptimeSec % 86400) / 3600);
        const mins = Math.floor((uptimeSec % 3600) / 60);
        const uptimeEl = document.getElementById('perf-uptime');
        if (uptimeEl) {
            let parts = [];
            if (days > 0) parts.push(`${days}d`);
            parts.push(`${String(hrs).padStart(2,'0')}h`);
            parts.push(`${String(mins).padStart(2,'0')}m`);
            uptimeEl.textContent = `Uptime: ${parts.join(' ')}`;
        }
    }
    const syncEl = document.getElementById('perf-last-sync');
    if (syncEl) {
        const now = new Date();
        syncEl.textContent = `Last Sync: ${now.toLocaleTimeString()}`;
    }
}

/**
 * Renders a bar chart inside a container from a rolling history array.
 * Uses the light-mode blueprint style: bg-{color}/20 base, bg-{color}/40 mid, bg-{color} for recent.
 * @param {string} containerId - DOM id of the graph container
 * @param {number[]} history - Array of 0-100 percentage values
 * @param {string} colorName - Tailwind color token name (e.g. 'primary', 'secondary')
 */
function renderBarGraph(containerId, history, colorName) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const len = history.length;
    
    // Only rebuild DOM if bar count changed (first render or history size change)
    if (container.children.length !== len) {
        let barsHtml = '';
        for (let i = 0; i < len; i++) {
            barsHtml += `<div class="w-full rounded-t-sm transition-all duration-500 ease-out" style="height: 0%"></div>`;
        }
        container.innerHTML = barsHtml;
    }
    
    const bars = container.children;
    for (let i = 0; i < len; i++) {
        const val = Math.max(0, Math.min(100, history[i]));
        const pct = Math.max(1, val); // minimum 1% height so bars are visible
        const bar = bars[i];
        
        // Determine opacity tier based on position (older = more transparent)
        const age = (i / len); // 0 = oldest, 1 = newest
        let opacity, bgColor;
        if (age > 0.85) {
            // Most recent bars: full/high opacity
            opacity = val > 50 ? 1.0 : 0.6;
            bgColor = `var(--tw-${colorName})`;
            bar.style.background = bgColor;
            bar.style.opacity = opacity;
        } else if (age > 0.5) {
            opacity = 0.35;
            bgColor = `var(--tw-${colorName})`;
            bar.style.background = bgColor;
            bar.style.opacity = opacity;
        } else {
            opacity = 0.18;
            bgColor = `var(--tw-${colorName})`;
            bar.style.background = bgColor;
            bar.style.opacity = opacity;
        }
        
        bar.style.height = `${pct}%`;
    }
}

// Generates the Tailwind grid row for a process
function createProcessRowHTML(proc, isApp) {
    const isSelected = proc.pid === selectedPid;
    let rowClass = 'grid grid-cols-[2fr_1fr_90px_100px_100px_100px] items-center px-6 py-3 hover:bg-surface-container-lowest transition-colors text-sm row-hover-advanced';
    
    if (isSelected) {
        rowClass += ' selected';
    }
    if (!isApp) {
        rowClass += 'opacity-80'; // Dim background processes
    }

    // Material Icon selection logic based on name
    let icon = 'wysiwyg';
    let iconClass = 'bg-primary/10 text-primary';
    
    let loweredName = proc.name.toLowerCase();
    if (loweredName.includes('brave') || loweredName.includes('chrome') || loweredName.includes('edge') || loweredName.includes('firefox')) {
        icon = 'language';
        iconClass = 'bg-orange-100 text-orange-600';
    } else if (loweredName.includes('spotify') || loweredName.includes('music')) {
        icon = 'music_note';
        iconClass = 'bg-green-100 text-green-600';
    } else if (loweredName.includes('python') || loweredName.includes('code')) {
        icon = 'terminal';
        iconClass = 'bg-blue-100 text-blue-600';
    }

    let iconHtml = '';
    if (isApp) {
        iconHtml = `
        <div class="w-5 h-5 ${iconClass} rounded flex items-center justify-center">
            <span class="material-symbols-outlined text-sm" data-icon="${icon}">${icon}</span>
        </div>`;
    } else {
        iconHtml = `<span class="material-symbols-outlined text-on-surface-variant text-[18px]" data-icon="settings_applications">settings_applications</span>`;
    }

    const cpuText = proc.cpu >= 0.1 ? proc.cpu.toFixed(1) + '%' : '0%';
    const cpuHtml = proc.cpu >= 2.0 
        ? `<div class="text-right font-bold text-primary bg-primary/10 rounded px-2 py-1 inline-block float-right">${cpuText}</div>`
        : `<div class="text-right font-medium">${cpuText}</div>`;

    let memText = `${proc.memory.toFixed(1)} MB`;
    if (proc.memory >= 1000) memText = `${(proc.memory / 1024).toFixed(1)} GB`;

    return `
    <div class="${rowClass}" onclick="selectProcess(${proc.pid})">
        <div class="flex items-center gap-3">
            <span class="material-symbols-outlined ${isSelected ? 'text-primary' : 'text-transparent'} text-[18px] transition-colors" data-icon="chevron_right">chevron_right</span>
            ${iconHtml}
            <span class="${isApp ? 'font-medium' : ''} text-on-surface">${proc.name} ${isApp ? `(${proc.threads})` : ''}</span>
        </div>
        <div class="text-on-surface-variant text-xs">${proc.status}</div>
        <div>${cpuHtml}</div>
        <div class="text-right text-on-surface-variant">${memText}</div>
        <div class="text-right text-on-surface-variant">0 MB/s</div>
        <div class="text-right text-on-surface-variant">0 Mbps</div>
    </div>`;
}

function renderProcesses() {
    if (!cachedState) return;

    const filterText = document.getElementById('search-input').value.toLowerCase();
    const listContainer = document.getElementById('process-list');
    
    let apps = [];
    let bg = [];
    
    cachedState.processes.forEach(proc => {
        if (filterText) {
            const matchString = `${proc.name} ${proc.pid}`.toLowerCase();
            if (!matchString.includes(filterText)) return;
        }
        if (proc.category === 'app') {
            apps.push(proc);
        } else {
            bg.push(proc);
        }
    });

    if (currentSort === 'cpu') {
        apps.sort((a, b) => b.cpu - a.cpu);
        bg.sort((a, b) => b.cpu - a.cpu);
    } else if (currentSort === 'memory') {
        apps.sort((a, b) => b.memory - a.memory);
        bg.sort((a, b) => b.memory - a.memory);
    } else {
        apps.sort((a, b) => a.name.localeCompare(b.name));
        bg.sort((a, b) => a.name.localeCompare(b.name));
    }

    let html = '';

    // Apps Section
    if (apps.length > 0) {
        const arrowRotation = appsCollapsed ? '-rotate-90' : '';
        html += `
        <div class="px-4 py-2 bg-surface-container-low/30 cursor-pointer select-none" onclick="toggleSection('apps')">
            <div class="flex items-center gap-2 text-xs font-bold text-on-surface-variant">
                <span class="material-symbols-outlined text-sm transition-transform duration-200 hover:bg-surface-variant rounded-full p-0.5 ${arrowRotation}" data-icon="expand_more">expand_more</span>
                Apps (${apps.length})
            </div>
        </div>`;
        if (!appsCollapsed) {
            apps.forEach(proc => {
                html += createProcessRowHTML(proc, true);
            });
        }
    }

    // BG Section
    if (bg.length > 0) {
        const arrowRotation = bgCollapsed ? '-rotate-90' : '';
        html += `
        <div class="px-4 py-2 bg-surface-container-low/30 mt-2 cursor-pointer select-none" onclick="toggleSection('bg')">
            <div class="flex items-center gap-2 text-xs font-bold text-on-surface-variant">
                <span class="material-symbols-outlined text-sm transition-transform duration-200 hover:bg-surface-variant rounded-full p-0.5 ${arrowRotation}" data-icon="expand_more">expand_more</span>
                Background processes (${bg.length})
            </div>
        </div>`;
        if (!bgCollapsed) {
            bg.forEach(proc => {
                html += createProcessRowHTML(proc, false);
            });
        }
    }

    listContainer.innerHTML = html;
}

function selectProcess(pid) {
    if (selectedPid === pid) {
        selectedPid = null;
        selectedName = null;
        selectedPids = [];
    } else {
        selectedPid = pid;
        // Find the process name and all PIDs
        if (cachedState) {
            const proc = cachedState.processes.find(p => p.pid === pid);
            selectedName = proc ? proc.name : null;
            selectedPids = proc ? (proc.pids || [pid]) : [pid];
        }
    }
    updateEndTaskButton();
    renderProcesses();
}

function updateEndTaskButton() {
    const btn = document.getElementById('btn-end-task');
    if (!btn) return;
    if (selectedPid !== null) {
        btn.disabled = false;
        btn.className = 'flex items-center gap-2 text-xs font-bold text-error hover:bg-error/10 px-4 py-2 rounded-lg transition-colors border border-error/20 btn-advanced shadow-sm cursor-pointer';
    } else {
        btn.disabled = true;
        btn.className = 'flex items-center gap-2 text-xs font-bold text-on-surface-variant/40 cursor-not-allowed px-4 py-2 rounded-lg border border-outline-variant/20 btn-advanced';
    }
}

document.getElementById('search-input').addEventListener('input', () => {
    renderProcesses();
});

// ── SPA View Switching Logic ──
function switchView(viewName) {
    const viewProcesses = document.getElementById('view-processes');
    const viewPerformance = document.getElementById('view-performance');
    const navProcesses = document.getElementById('nav-processes');
    const navPerformance = document.getElementById('nav-performance');
    const mobProcesses = document.getElementById('mob-nav-processes');
    const mobPerformance = document.getElementById('mob-nav-performance');

    if (viewName === 'processes') {
        viewProcesses.classList.remove('hidden');
        viewPerformance.classList.add('hidden');
        
        // Desktop Nav State
        navProcesses.className = "flex w-full items-center gap-4 bg-primary text-white rounded-full px-6 py-3 mx-4 my-2 font-['Manrope'] font-medium shadow-md btn-advanced nav-active-pulse";
        navPerformance.className = "flex w-full items-center gap-4 text-on-surface-variant px-6 py-3 mx-4 my-2 font-['Manrope'] font-medium hover:bg-surface-container transition-colors rounded-full btn-advanced";
        
        // Mobile Nav State
        mobProcesses.className = "flex flex-col items-center gap-1 text-primary btn-hover-effect active-pulse";
        mobPerformance.className = "flex flex-col items-center gap-1 text-on-surface-variant btn-hover-effect";

        renderProcesses();
        
    } else if (viewName === 'performance') {
        viewPerformance.classList.remove('hidden');
        viewProcesses.classList.add('hidden');
        
        // Desktop Nav State
        navPerformance.className = "flex w-full items-center gap-4 bg-primary text-white rounded-full px-6 py-3 mx-4 my-2 font-['Manrope'] font-medium shadow-md btn-advanced nav-active-pulse";
        navProcesses.className = "flex w-full items-center gap-4 text-on-surface-variant px-6 py-3 mx-4 my-2 font-['Manrope'] font-medium hover:bg-surface-container transition-colors rounded-full btn-advanced";
        
        // Mobile Nav State
        mobPerformance.className = "flex flex-col items-center gap-1 text-primary btn-hover-effect active-pulse";
        mobProcesses.className = "flex flex-col items-center gap-1 text-on-surface-variant btn-hover-effect";
    }
}


// ── Snapshot System ──
async function snapshotSystem() {
    try {
        const res = await fetch('/api/snapshot');
        const data = await res.json();
        
        // Create a downloadable JSON file
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        a.href = url;
        a.download = `snapshot_${ts}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast(`System snapshot saved (${data.summary.total_processes} processes captured).`, 'success');
    } catch (err) {
        showToast('Failed to capture snapshot.', 'error');
    }
}


// ── Toast Notification System ──
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const bgColor = type === 'success' ? 'bg-primary' : 'bg-error';
    const icon = type === 'success' ? 'check_circle' : 'error';
    
    const toast = document.createElement('div');
    toast.className = `${bgColor} text-white px-5 py-3 rounded-xl shadow-xl flex items-center gap-3 text-sm font-medium animate-entrance max-w-sm`;
    toast.innerHTML = `<span class="material-symbols-outlined text-sm">${icon}</span> ${message}`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ── Run Task Modal ──
function openRunTaskModal() {
    const modal = document.getElementById('run-task-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    setTimeout(() => document.getElementById('run-task-input').focus(), 100);
}

function closeRunTaskModal() {
    const modal = document.getElementById('run-task-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.getElementById('run-task-input').value = '';
}

async function executeRunTask() {
    const input = document.getElementById('run-task-input');
    const command = input.value.trim();
    if (!command) {
        input.focus();
        return;
    }
    
    try {
        const res = await fetch('/api/run-task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        });
        const data = await res.json();
        
        if (data.status === 'ok') {
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (err) {
        showToast('Failed to connect to server.', 'error');
    }
    
    closeRunTaskModal();
}

// ── End Task ──
function endSelectedTask() {
    if (selectedPid === null || selectedPids.length === 0) return;
    openEndTaskModal();
}

function openEndTaskModal() {
    const modal = document.getElementById('end-task-modal');
    const msg = document.getElementById('end-task-msg');
    const name = selectedName || `PID ${selectedPid}`;
    msg.textContent = `Are you sure you want to end "${name}"? Unsaved data may be lost.`;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeEndTaskModal() {
    const modal = document.getElementById('end-task-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

async function confirmEndTask() {
    closeEndTaskModal();
    
    try {
        const res = await fetch('/api/end-task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pids: selectedPids, name: selectedName || '' })
        });
        const data = await res.json();
        
        if (data.status === 'ok') {
            showToast(data.message, 'success');
            selectedPid = null;
            selectedName = null;
            selectedPids = [];
            updateEndTaskButton();
        } else {
            showToast(data.message, 'error');
        }
    } catch (err) {
        showToast('Failed to connect to server.', 'error');
    }
}

// ── More Menu ──
function toggleMoreMenu() {
    const menu = document.getElementById('more-menu');
    menu.classList.toggle('hidden');
}

function refreshProcessList() {
    document.getElementById('more-menu').classList.add('hidden');
    renderProcesses();
    showToast('Process list refreshed.', 'success');
}

function sortByCPU() {
    document.getElementById('more-menu').classList.add('hidden');
    currentSort = currentSort === 'cpu' ? 'name' : 'cpu';
    renderProcesses();
    showToast(currentSort === 'cpu' ? 'Sorted by CPU usage.' : 'Sorted by name.', 'success');
}

function sortByMemory() {
    document.getElementById('more-menu').classList.add('hidden');
    currentSort = currentSort === 'memory' ? 'name' : 'memory';
    renderProcesses();
    showToast(currentSort === 'memory' ? 'Sorted by memory usage.' : 'Sorted by name.', 'success');
}

// Close more menu on outside click
document.addEventListener('click', (e) => {
    const menu = document.getElementById('more-menu');
    const btn = document.getElementById('btn-more');
    if (menu && btn && !menu.contains(e.target) && !btn.contains(e.target)) {
        menu.classList.add('hidden');
    }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeRunTaskModal();
        closeEndTaskModal();
        document.getElementById('more-menu')?.classList.add('hidden');
    }
});

// ── Theme Switching Logic ──
document.getElementById('theme-toggle').addEventListener('click', () => {
    const htmlEl = document.documentElement;
    const btnIcon = document.querySelector('#theme-toggle .material-symbols-outlined');
    if (htmlEl.classList.contains('dark')) {
        htmlEl.classList.remove('dark');
        btnIcon.textContent = 'light_mode';
        localStorage.theme = 'light';
    } else {
        htmlEl.classList.add('dark');
        btnIcon.textContent = 'dark_mode';
        localStorage.theme = 'dark';
    }
});

// Force light mode as default and restore saved theme on load
const savedTheme = localStorage.theme;
if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark');
    document.documentElement.classList.remove('light');
    const btnIcon = document.querySelector('#theme-toggle .material-symbols-outlined');
    if (btnIcon) btnIcon.textContent = 'dark_mode';
} else {
    // Force light mode by default
    document.documentElement.classList.remove('dark');
    document.documentElement.classList.add('light');
    const btnIcon = document.querySelector('#theme-toggle .material-symbols-outlined');
    if (btnIcon) btnIcon.textContent = 'light_mode';
    localStorage.theme = 'light';
}
