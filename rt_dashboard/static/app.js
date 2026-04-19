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
    if (!document.getElementById('processes-tab').classList.contains('hidden-tab')) {
        renderProcesses();
    }
};


let cpuPeak = 0;
let prevCpu = 0;

const metricHistory = { cpu: [], mem: [], disk: [], net: [] };
const HISTORY_MAX = 20;


function updateMetrics(state) {
    // Top summary bar in Footer
    const sumCpu = document.getElementById('sum-cpu');
    if(sumCpu) sumCpu.textContent = `${Math.round(state.cpu_percent)}%`;
    const sumMem = document.getElementById('sum-mem');
    if(sumMem) sumMem.textContent = `${Math.round(state.ram_percent)}%`;

    const diskTotal = state.disk_read_rate + state.disk_write_rate;
    const netTotal = state.net_sent_rate + state.net_recv_rate;

    // Push to History
    metricHistory.cpu.push(state.cpu_percent);
    metricHistory.mem.push(state.ram_used);
    
    // Normalize disk to a 0-100 scale approximately (assuming 500MB/s is 100% for visual sake)
    const diskMax = 500;
    metricHistory.disk.push(Math.min(100, (diskTotal / diskMax) * 100));
    
    // Normalize net to a 0-100 scale (assuming 10000KB/s is 100%)
    const netMax = 10000;
    metricHistory.net.push(Math.min(100, (netTotal / netMax) * 100));

    if (metricHistory.cpu.length > HISTORY_MAX) {
        metricHistory.cpu.shift();
        metricHistory.mem.shift();
        metricHistory.disk.shift();
        metricHistory.net.shift();
    }

    renderBarGraph('.graph-container-cpu', metricHistory.cpu, 'primary');
    // Memory uses ram_percent for the bar graph height (so map it 0-100)
    renderBarGraph('.graph-container-mem', metricHistory.mem.map(v => (v / state.ram_total) * 100), 'secondary');
    renderBarGraph('.graph-container-disk', metricHistory.disk, 'tertiary');
    renderBarGraph('.graph-container-net', metricHistory.net, 'outline');

    // ── Update Bento Grid Cards (both in Processes and Performance tabs) ──
    // CPU Card
    const cpuCards = document.querySelectorAll('.text-metric-cpu');
    cpuCards.forEach(icon => {
        const valueContainer = icon.closest('.glass-card').querySelector('.font-headline');
        if (valueContainer) {
            valueContainer.innerHTML = `${Math.round(state.cpu_percent)}<span class="text-xl text-outline-variant">%</span>`;
        }
        const descContainer = icon.closest('.glass-card').querySelector('.font-body');
        if (descContainer) {
            descContainer.textContent = `Active processing load`;
        }
    });

    // RAM Card
    const memCards = document.querySelectorAll('.text-metric-mem');
    memCards.forEach(icon => {
        const valueContainer = icon.closest('.glass-card').querySelector('.font-headline');
        if (valueContainer) {
            valueContainer.innerHTML = `${state.ram_used.toFixed(1)}<span class="text-xl text-outline-variant">GB</span>`;
        }
        const descContainer = icon.closest('.glass-card').querySelector('.font-body');
        if (descContainer) {
            descContainer.textContent = `${Math.round(state.ram_percent)}% of total capacity`;
        }
    });

    // Disk Card
    const diskCards = document.querySelectorAll('.text-metric-disk');
    diskCards.forEach(icon => {
        const valueContainer = icon.closest('.glass-card').querySelector('.font-headline');
        if (valueContainer) {
            valueContainer.innerHTML = `${diskTotal.toFixed(1)}<span class="text-xl text-outline-variant">MB/s</span>`;
        }
        const descContainer = icon.closest('.glass-card').querySelector('.font-body');
        if (descContainer) {
            descContainer.textContent = `R: ${state.disk_read_rate.toFixed(1)} W: ${state.disk_write_rate.toFixed(1)}`;
        }
    });

    // Network Card
    const netCards = document.querySelectorAll('.text-metric-net');
    netCards.forEach(icon => {
        const valueContainer = icon.closest('.glass-card').querySelector('.font-headline');
        if (valueContainer) {
            valueContainer.innerHTML = `${Math.round(netTotal)}<span class="text-xl text-outline-variant">KB/s</span>`;
        }
        const descContainer = icon.closest('.glass-card').querySelector('.font-body');
        if (descContainer) {
            descContainer.textContent = `↑ ${state.net_sent_rate.toFixed(1)} ↓ ${state.net_recv_rate.toFixed(1)}`;
        }
    });

    // ── Update Live Analytics ──
    const safeMax = arr => arr.length ? Math.max(...arr) : 0;
    const safeAvg = arr => arr.length ? (arr.reduce((a,b)=>a+b, 0) / arr.length) : 0;

    const elCpuVal = document.getElementById('perf-cpu-val');
    const elCpuPeak = document.getElementById('perf-cpu-peak');
    const elCpuAvg = document.getElementById('perf-cpu-avg');
    if(elCpuVal) elCpuVal.textContent = state.cpu_percent.toFixed(1);
    if(elCpuPeak) elCpuPeak.textContent = safeMax(metricHistory.cpu).toFixed(1) + '%';
    if(elCpuAvg) elCpuAvg.textContent = safeAvg(metricHistory.cpu).toFixed(1) + '%';

    const elMemVal = document.getElementById('perf-mem-val');
    const elMemPeak = document.getElementById('perf-mem-peak');
    const elMemAvg = document.getElementById('perf-mem-avg');
    if(elMemVal) elMemVal.textContent = state.ram_used.toFixed(1);
    if(elMemPeak) elMemPeak.textContent = safeMax(metricHistory.mem).toFixed(1) + ' GB';
    if(elMemAvg) elMemAvg.textContent = safeAvg(metricHistory.mem).toFixed(1) + ' GB';

    const elDiskVal = document.getElementById('perf-disk-val');
    const elDiskWrite = document.getElementById('perf-disk-write');
    const elDiskRead = document.getElementById('perf-disk-read');
    if(elDiskVal) elDiskVal.textContent = diskTotal.toFixed(0);
    if(elDiskWrite) elDiskWrite.textContent = state.disk_write_rate.toFixed(1) + ' MB/s';
    if(elDiskRead) elDiskRead.textContent = state.disk_read_rate.toFixed(1) + ' MB/s';

    const elNetVal = document.getElementById('perf-net-val');
    const elNetDown = document.getElementById('perf-net-down');
    const elNetUp = document.getElementById('perf-net-up');
    if(elNetVal) elNetVal.textContent = Math.round(state.net_recv_rate + state.net_sent_rate);
    if(elNetDown) elNetDown.textContent = state.net_recv_rate.toFixed(1) + ' KB/s';
    if(elNetUp) elNetUp.textContent = state.net_sent_rate.toFixed(1) + ' KB/s';
    const elNetTotal = document.getElementById('perf-net-total');
    if(elNetTotal) elNetTotal.textContent = (state.net_recv_rate + state.net_sent_rate).toFixed(1) + ' KB/s';

    // ── Uptime ──
    if (state.boot_time) {
        const uptimeSec = Math.floor(Date.now() / 1000 - state.boot_time);
        const days = Math.floor(uptimeSec / 86400);
        const hrs  = Math.floor((uptimeSec % 86400) / 3600);
        const mins = Math.floor((uptimeSec % 3600) / 60);
        const uptimeEl = document.getElementById('perf-uptime');
        if (uptimeEl) {
            let parts = [];
            if (days > 0) parts.push(`${days}d`);
            parts.push(`${String(hrs).padStart(2,'0')}:${String(mins).padStart(2,'0')}`);
            uptimeEl.textContent = parts.join(' ');
        }
    }
}


/**
 * Renders a bar chart inside a container from a rolling history array.
 * Uses the light-mode blueprint style: bg-{color}/20 base, bg-{color}/40 mid, bg-{color} for recent.
 * @param {string} containerId - DOM id of the graph container
 * @param {number[]} history - Array of 0-100 percentage values
 * @param {string} colorName - Tailwind color token name (e.g. 'primary', 'secondary')
 */
function renderBarGraph(containerSelector, history, colorName) {
    const containers = document.querySelectorAll(containerSelector);
    if (containers.length === 0) return;
    
    const len = history.length;
    
    containers.forEach(container => {
        // Only rebuild DOM if bar count changed
        if (container.children.length !== len) {
            let barsHtml = '';
            for (let i = 0; i < len; i++) {
                barsHtml += `<div class="flex-1 min-w-[6px] rounded-t-sm transition-all duration-500 ease-out" style="height: 0%"></div>`;
            }
            container.innerHTML = barsHtml;
        }
        
        const bars = container.children;
        for (let i = 0; i < len; i++) {
            const val = Math.max(0, Math.min(100, history[i]));
            const pct = Math.max(1, val); 
            const bar = bars[i];
            
            const age = (i / len);
            let opacity, bgColor;
            
            // For the custom tailwind colors, use standard tailwind arbitrary opacity syntax or just raw classes
            // Our index.html has var(--theme-...) so it's safer to use the standard colors directly if we want
            // but the original code used `bg-${colorName}-fixed-dim`. We'll keep it as is, since our 
            // python script generated --theme-primary-bg etc instead of Tailwind classes for everything.
            // Wait, we can just use `bg-[var(--theme-${colorName}-text)]`!
            
            // Map colorName to CSS variables injected in index.html
            const themeColorMap = {
                'primary': '--theme-primary-text',
                'secondary': '--theme-secondary-dim-text',
                'tertiary': '--theme-tertiary-text',
                'outline': '--theme-secondary-text' 
            };
            
            let colorVar = themeColorMap[colorName] || '--theme-primary-text';
            
            if (age < 0.33) {
                opacity = 0.2;
            } else if (age < 0.66) {
                opacity = 0.4;
            } else {
                opacity = 0.8; 
            }
            
            // To ensure compatibility across both themes, set background color via inline style
            // using the CSS variables.
            bar.className = `w-full rounded-t-sm transition-all duration-500 ease-out`;
            bar.style.height = `${pct}%`;
            bar.style.backgroundColor = `var(${colorVar})`;
            bar.style.opacity = opacity;
        }
    });
}

// Generates the Tailwind grid row for a process

function createProcessRowHTML(proc, isApp) {
    const isSelected = proc.pid === selectedPid;
    let rowClass = 'transition-colors group';
    if (isSelected) {
        rowClass += ' bg-white/10 border-l-2 border-primary-fixed-dim'; 
    } else {
        rowClass += ' hover:bg-white/10';
    }

    let icon = 'settings_applications';
    let iconClass = 'bg-outline-variant/10 text-outline-variant border-outline-variant/20';
    if (isApp) {
        icon = 'wysiwyg';
        iconClass = 'bg-primary-fixed-dim/20 text-primary-fixed-dim border-primary-fixed-dim/30';
        let loweredName = proc.name.toLowerCase();
        if (loweredName.includes('brave') || loweredName.includes('chrome') || loweredName.includes('edge') || loweredName.includes('firefox')) {
            icon = 'language';
            iconClass = 'bg-orange-500/20 text-orange-400 border-orange-500/30';
        } else if (loweredName.includes('spotify') || loweredName.includes('music')) {
            icon = 'music_note';
            iconClass = 'bg-green-500/20 text-green-400 border-green-500/30';
        } else if (loweredName.includes('python') || loweredName.includes('code')) {
            icon = 'terminal';
            iconClass = 'bg-blue-500/20 text-blue-400 border-blue-500/30';
        }
    }

    let statusHtml = '<span class="px-2 py-0.5 rounded text-[10px] font-label uppercase tracking-wider bg-outline-variant/10 text-outline-variant border border-outline-variant/20">Background</span>';
    if (proc.status.toLowerCase().includes('running')) {
        statusHtml = '<span class="px-2 py-0.5 rounded text-[10px] font-label uppercase tracking-wider bg-tertiary-fixed-dim/10 text-tertiary-fixed-dim border border-tertiary-fixed-dim/20">Stable</span>';
    } else if (proc.status.toLowerCase().includes('not responding')) {
        statusHtml = '<span class="px-2 py-0.5 rounded text-[10px] font-label uppercase tracking-wider bg-error-container/10 text-error border border-error/20 status-critical">Critical</span>';
    } else if (proc.status.toLowerCase().includes('suspended')) {
        statusHtml = '<span class="px-2 py-0.5 rounded text-[10px] font-label uppercase tracking-wider bg-secondary-container/10 text-secondary-container border border-secondary-container/20 status-warning">Suspended</span>';
    }

    if (proc.cpu > 10) {
        statusHtml = '<span class="px-2 py-0.5 rounded text-[10px] font-label uppercase tracking-wider bg-error-container/10 text-error border border-error/20 status-critical">High Load</span>';
    }

    const cpuText = proc.cpu >= 0.1 ? proc.cpu.toFixed(1) + '%' : '0%';
    let memText = `${proc.memory.toFixed(1)} MB`;
    if (proc.memory >= 1000) memText = `${(proc.memory / 1024).toFixed(1)} GB`;

    return `
    <tr class="${rowClass} hover:bg-primary/10 dark:hover:bg-white/10 transition-colors group cursor-pointer border-b border-white/10 dark:border-white/5" id="proc-${proc.pid}" onclick="selectProcess(${proc.pid})">
        <td class="px-6 py-4 text-outline-variant font-mono">${proc.pid}</td>
        <td class="px-6 py-4 font-semibold flex items-center gap-3">
            <div class="w-8 h-8 shrink-0 rounded flex items-center justify-center border ${iconClass}">
                <span class="material-symbols-outlined text-sm">${icon}</span>
            </div>
            <span class="truncate">${proc.name} ${isApp ? `(${proc.threads})` : ''}</span>
        </td>
        <td class="px-6 py-4">${statusHtml}</td>
        <td class="px-6 py-4 text-metric-unified font-mono font-medium">${cpuText}</td>
        <td class="px-6 py-4 text-metric-unified font-mono font-medium">${memText}</td>
        <td class="px-6 py-4 text-metric-unified font-mono font-medium">0 MB/s</td>
        <td class="px-6 py-4 text-metric-unified font-mono font-medium">0 Kbps</td>
    </tr>`;
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
        <tr class="bg-white/5 cursor-pointer select-none" onclick="toggleSection('apps')">
            <td colspan="7" class="px-6 py-2 text-xs font-bold text-outline-variant border-y border-white/5">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-sm transition-transform duration-200 hover:text-white ${arrowRotation}">expand_more</span>
                    Apps (${apps.length})
                </div>
            </td>
        </tr>`;

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
        <tr class="bg-white/5 cursor-pointer select-none" onclick="toggleSection('bg')">
            <td colspan="7" class="px-6 py-2 text-xs font-bold text-outline-variant border-y border-white/5">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-sm transition-transform duration-200 hover:text-white ${arrowRotation}">expand_more</span>
                    Background processes (${bg.length})
                </div>
            </td>
        </tr>`;

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
        btn.className = 'flex items-center gap-2 px-3 py-1.5 rounded-lg bg-error/20 border border-error/50 backdrop-blur-md text-xs font-semibold text-error transition-all hover:scale-105 shadow-[0_0_15px_rgba(186,26,26,0.4)]';
    } else {
        btn.disabled = true;
        btn.className = 'flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--theme-glass)] border border-[var(--theme-border-strong)] backdrop-blur-md text-xs font-semibold text-[var(--theme-text-muted)] transition-all cursor-not-allowed';
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
