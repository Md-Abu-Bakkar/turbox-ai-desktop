// TurboX DevTools Pro - Popup Script
// Controls the extension popup interface

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Show corresponding content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
        });
    });
    
    // State
    let state = {
        desktopConnected: false,
        capturing: false,
        activeTools: 0,
        capturedRequests: 0,
        smsMessages: 0,
        activeSessions: []
    };
    
    // Initialize
    updateStatus();
    loadSettings();
    loadSessions();
    
    // Check desktop connection
    checkDesktopConnection();
    
    // Update status periodically
    setInterval(updateStatus, 3000);
    
    // Toggle network capture
    const toggleCapture = document.getElementById('toggle-capture');
    toggleCapture.addEventListener('change', function() {
        state.capturing = this.checked;
        updateCaptureStatus();
        
        chrome.runtime.sendMessage({
            type: 'TOGGLE_CAPTURE',
            enabled: state.capturing
        });
    });
    
    // Launch tools button
    document.getElementById('launch-tools').addEventListener('click', function() {
        chrome.runtime.sendMessage({
            type: 'LAUNCH_TOOLS',
            tools: ['api_tester', 'sms_panel']
        });
        
        showNotification('Launching desktop tools...');
    });
    
    // Export data button
    document.getElementById('export-data').addEventListener('click', function() {
        chrome.runtime.sendMessage({
            type: 'EXPORT_DATA_REQUEST',
            format: 'json'
        });
        
        showNotification('Exporting data...');
    });
    
    // Auto-login button
    document.getElementById('auto-login').addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                type: 'AUTO_LOGIN_REQUEST'
            });
        });
        
        showNotification('Attempting auto-login...');
    });
    
    // Clear data button
    document.getElementById('clear-data').addEventListener('click', function() {
        if (confirm('Clear all captured data?')) {
            chrome.runtime.sendMessage({
                type: 'CLEAR_DATA'
            });
            
            state.capturedRequests = 0;
            state.smsMessages = 0;
            updateStats();
            
            showNotification('Data cleared');
        }
    });
    
    // Export buttons
    document.querySelectorAll('.export-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const format = this.getAttribute('data-format');
            
            chrome.runtime.sendMessage({
                type: 'EXPORT_DATA_REQUEST',
                format: format
            });
            
            showNotification(`Exporting as ${format.toUpperCase()}...`);
        });
    });
    
    // Automation toggles
    document.getElementById('toggle-auto-launch').addEventListener('change', function() {
        saveSetting('auto_launch', this.checked);
    });
    
    document.getElementById('toggle-auto-captcha').addEventListener('change', function() {
        saveSetting('auto_captcha', this.checked);
    });
    
    document.getElementById('toggle-auto-session').addEventListener('change', function() {
        saveSetting('auto_session', this.checked);
    });
    
    document.getElementById('toggle-auto-export').addEventListener('change', function() {
        saveSetting('auto_export', this.checked);
    });
    
    // Automation buttons
    document.getElementById('scan-page').addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                type: 'SCAN_PAGE'
            });
        });
        
        showNotification('Scanning page...');
    });
    
    document.getElementById('extract-data').addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                type: 'EXTRACT_DATA'
            });
        });
        
        showNotification('Extracting data...');
    });
    
    document.getElementById('monitor-page').addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                type: 'MONITOR_PAGE'
            });
        });
        
        showNotification('Monitoring page...');
    });
    
    document.getElementById('run-script').addEventListener('click', function() {
        const script = prompt('Enter JavaScript to run on page:');
        if (script) {
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                chrome.tabs.sendMessage(tabs[0].id, {
                    type: 'RUN_SCRIPT',
                    script: script
                });
            });
        }
    });
    
    // Session buttons
    document.getElementById('refresh-sessions').addEventListener('click', loadSessions);
    document.getElementById('export-sessions').addEventListener('click', exportSessions);
    
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
        switch (message.type) {
            case 'STATUS_UPDATE':
                state.desktopConnected = message.desktopConnected || false;
                state.capturedRequests = message.capturedRequests || 0;
                state.smsMessages = message.smsMessages || 0;
                state.activeTools = message.activeTools || 0;
                updateStatusDisplay();
                break;
                
            case 'DATA_EXPORTED':
                showNotification(`Data exported: ${message.filename}`);
                break;
                
            case 'AUTOMATION_LOG':
                addToAutomationLog(message.message);
                break;
                
            case 'SESSION_UPDATE':
                state.activeSessions = message.sessions || [];
                updateSessionsList();
                break;
        }
    });
    
    // Functions
    function updateStatus() {
        // Get current status from background script
        chrome.runtime.sendMessage({type: 'GET_STATUS'}, function(response) {
            if (response) {
                state.desktopConnected = response.desktopConnected || false;
                state.capturing = response.capturing || false;
                state.capturedRequests = response.capturedRequests || 0;
                state.smsMessages = response.smsMessages || 0;
                state.activeTools = response.activeTools || 0;
                
                updateStatusDisplay();
                updateStats();
            }
        });
    }
    
    function updateStatusDisplay() {
        // Desktop connection
        const desktopStatus = document.getElementById('desktop-status');
        const desktopStatusText = document.getElementById('desktop-status-text');
        
        if (state.desktopConnected) {
            desktopStatus.className = 'connection-indicator connected';
            desktopStatusText.textContent = 'Connected';
            desktopStatusText.className = 'status-value status-connected';
        } else {
            desktopStatus.className = 'connection-indicator disconnected';
            desktopStatusText.textContent = 'Disconnected';
            desktopStatusText.className = 'status-value status-disconnected';
        }
        
        // Capture status
        const captureStatus = document.getElementById('capture-status');
        const toggleCapture = document.getElementById('toggle-capture');
        
        if (state.capturing) {
            captureStatus.className = 'capture-indicator capture-active';
            toggleCapture.checked = true;
        } else {
            captureStatus.className = 'capture-indicator capture-inactive';
            toggleCapture.checked = false;
        }
        
        // Active tools
        document.getElementById('active-tools').textContent = state.activeTools;
        document.getElementById('captured-count').textContent = state.capturedRequests;
        document.getElementById('sms-count').textContent = state.smsMessages;
    }
    
    function updateStats() {
        document.getElementById('stat-requests').textContent = state.capturedRequests;
        document.getElementById('stat-sms').textContent = state.smsMessages;
        document.getElementById('stat-sessions').textContent = state.activeSessions.length;
        
        // Get CAPTCHA count from storage
        chrome.storage.local.get(['captchaCount'], function(result) {
            const captchaCount = result.captchaCount || 0;
            document.getElementById('stat-captchas').textContent = captchaCount;
        });
    }
    
    function updateCaptureStatus() {
        const captureStatus = document.getElementById('capture-status');
        
        if (state.capturing) {
            captureStatus.className = 'capture-indicator capture-active';
        } else {
            captureStatus.className = 'capture-indicator capture-inactive';
        }
    }
    
    function checkDesktopConnection() {
        // Try to connect to desktop socket bridge
        fetch('http://localhost:8765/status')
            .then(response => response.json())
            .then(data => {
                state.desktopConnected = data.status === 'active';
                updateStatusDisplay();
            })
            .catch(() => {
                state.desktopConnected = false;
                updateStatusDisplay();
            });
    }
    
    function loadSettings() {
        chrome.storage.local.get(['turboXSettings'], function(result) {
            const settings = result.turboXSettings || {};
            
            document.getElementById('toggle-auto-launch').checked = settings.auto_launch !== false;
            document.getElementById('toggle-auto-captcha').checked = settings.auto_captcha !== false;
            document.getElementById('toggle-auto-session').checked = settings.auto_session !== false;
            document.getElementById('toggle-auto-export').checked = settings.auto_export || false;
        });
    }
    
    function saveSetting(key, value) {
        chrome.storage.local.get(['turboXSettings'], function(result) {
            const settings = result.turboXSettings || {};
            settings[key] = value;
            
            chrome.storage.local.set({turboXSettings: settings});
            
            // Also send to background script
            chrome.runtime.sendMessage({
                type: 'UPDATE_SETTING',
                key: key,
                value: value
            });
        });
    }
    
    function loadSessions() {
        chrome.runtime.sendMessage({type: 'GET_SESSIONS'}, function(response) {
            if (response && response.sessions) {
                state.activeSessions = response.sessions;
                updateSessionsList();
            }
        });
    }
    
    function updateSessionsList() {
        const sessionsList = document.getElementById('sessions-list');
        
        if (state.activeSessions.length === 0) {
            sessionsList.innerHTML = '<div class="empty-state">No active sessions</div>';
            return;
        }
        
        sessionsList.innerHTML = '';
        
        state.activeSessions.forEach(session => {
            const sessionItem = document.createElement('div');
            sessionItem.className = 'session-item';
            
            const domain = session.domain || 'Unknown';
            const username = session.username || 'No username';
            const lastUsed = session.last_used ? 
                new Date(session.last_used).toLocaleTimeString() : 'Unknown';
            
            sessionItem.innerHTML = `
                <div class="session-domain">${domain}</div>
                <div class="session-info">
                    <span>${username}</span>
                    <span>${lastUsed}</span>
                </div>
            `;
            
            sessionsList.appendChild(sessionItem);
        });
    }
    
    function exportSessions() {
        chrome.runtime.sendMessage({
            type: 'EXPORT_SESSIONS',
            format: 'json'
        });
        
        showNotification('Exporting sessions...');
    }
    
    function addToAutomationLog(message) {
        const logElement = document.getElementById('automation-log');
        
        if (logElement.classList.contains('empty-state')) {
            logElement.classList.remove('empty-state');
            logElement.innerHTML = '';
        }
        
        const logEntry = document.createElement('div');
        logEntry.className = 'session-item';
        logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        
        logElement.prepend(logEntry);
        
        // Keep only last 10 entries
        const entries = logElement.querySelectorAll('.session-item');
        if (entries.length > 10) {
            entries[entries.length - 1].remove();
        }
    }
    
    function showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'session-item';
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.left = '50%';
        notification.style.transform = 'translateX(-50%)';
        notification.style.zIndex = '1000';
        notification.style.background = 'rgba(29, 209, 161, 0.9)';
        notification.style.color = 'white';
        notification.style.padding = '10px 20px';
        notification.style.borderRadius = '4px';
        notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Initial updates
    updateStatusDisplay();
    updateStats();
});
