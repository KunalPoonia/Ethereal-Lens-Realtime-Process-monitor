let selectedPid = null;
let cachedState = null;

// Connect to the FastAPI WebSocket
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${location.host}/ws`);
const statusDiv = document.getElementById('connection-status');

ws.onopen = () => {
    statusDiv.textContent = 'Live';
    statusDiv.style.color = 'var(--c-dark-charcoal)';
};

ws.onclose = () => {
    statusDiv.textContent = 'Disconnected';
    statusDiv.style.color = 'var(--c-mid-grey)';
};

ws.onmessage = (event) => {
    cachedState = JSON.parse(event.data);
    updateMetrics(cachedState);
    renderProcesses();
};

function updateMetrics(state) {
    document.getElementById('val-cpu').textContent = `${Math.round(state.cpu_percent)}%`;
    document.getElementById('val-mem').textContent = `${state.ram_used.toFixed(1)} GB`;
    
    // Total disk IO in MB/s
    const diskTotal = state.disk_read_rate + state.disk_write_rate;
    document.getElementById('val-disk').textContent = `${diskTotal.toFixed(1)} MB/s`;
    
    // Total Network in KB/s
    const netTotal = state.net_sent_rate + state.net_recv_rate;
    document.getElementById('val-net').textContent = `${Math.round(netTotal)} KB/s`;
}

// ── Heatmap Generator ──
// Strictly maps to White, Light Grey, Mid Grey, and Charcoal
function getHeatmapColor(percent) {
    if (percent < 2) return 'transparent';
    if (percent < 8) return '#D4D4D440'; // Tinge of Light Grey
    if (percent < 25) return '#B3B3B380'; // 50% Mid Grey
    if (percent < 50) return '#2B2B2B40'; // 25% Charcoal
    if (percent < 80) return '#2B2B2B80'; // 50% Charcoal
    return '#2B2B2B'; // Solid Charcoal
}

function renderProcesses() {
    if (!cachedState) return;

    const filterText = document.getElementById('search-input').value.toLowerCase();
    const tbody = document.getElementById('process-list');
    const processes = cachedState.processes;
    
    let html = '';
    
    // Sort processes alphabetically by name
    processes.sort((a, b) => a.name.localeCompare(b.name));

    processes.forEach(proc => {
        // Search Filter Logic
        if (filterText) {
            const matchString = `${proc.name} ${proc.pid}`.toLowerCase();
            if (!matchString.includes(filterText)) return;
        }

        const isSelected = proc.pid === selectedPid;
        const rowClass = isSelected ? 'process-row selected' : 'process-row';
        
        // Heatmap for CPU
        const cpuColor = getHeatmapColor(proc.cpu);
        const cpuText = proc.cpu >= 0.1 ? `${proc.cpu.toFixed(1)}%` : '<span class="text-muted">0%</span>';
        
        // Heatmap for Memory (max 4096 MB for scaling baseline)
        const memScale = (proc.memory / 4096) * 100;
        const memColor = getHeatmapColor(memScale);
        
        let memText = `${proc.memory.toFixed(1)} MB`;
        if (proc.memory >= 1000) memText = `${(proc.memory / 1024).toFixed(1)} GB`;

        html += `
            <tr class="${rowClass}" onclick="selectProcess(${proc.pid})">
                <td class="col-name">${proc.name}</td>
                <td class="text-muted">${proc.pid}</td>
                <td><span class="heat-pill" style="background-color: ${cpuColor}">${cpuText}</span></td>
                <td><span class="heat-pill" style="background-color: ${memColor}">${memText}</span></td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// ── Interactivity ──

// Instant Selection Feedback
function selectProcess(pid) {
    if (selectedPid === pid) {
        selectedPid = null;
    } else {
        selectedPid = pid;
    }
    renderProcesses(); // Instant DOM update relying on cachedState
}

// Instant Search Filtering
document.getElementById('search-input').addEventListener('input', () => {
    renderProcesses();
});
