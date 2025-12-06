// TurboX DevTools Pro - Content Script
// Phase 3: Enhanced Automation & Integration

// Communication with background script
const port = chrome.runtime.connect({name: "content-script"});

// State
let isActive = false;
let isCapturing = false;
let currentSession = null;
let capturedRequests = [];

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    switch (message.type) {
        case 'TOGGLE_CAPTURE':
            isCapturing = message.enabled;
            console.log(`📡 Capture ${isCapturing ? 'enabled' : 'disabled'}`);
            sendResponse({success: true});
            break;
            
        case 'TOGGLE_ACTIVE':
            isActive = message.enabled;
            if (isActive) {
                initializeAutomation();
            }
            sendResponse({success: true});
            break;
            
        case 'SET_SESSION':
            currentSession = message.session;
            console.log(`🔐 Session set for ${currentSession?.domain || 'unknown'}`);
            sendResponse({success: true});
            break;
            
        case 'EXECUTE_AUTOMATION':
            executeAutomation(message.script);
            sendResponse({success: true});
            break;
            
        case 'GET_PAGE_INFO':
            const pageInfo = getPageInfo();
            sendResponse(pageInfo);
            break;
            
        default:
            sendResponse({error: 'Unknown message type'});
    }
    
    return true; // Keep message channel open for async responses
});

// Initialize automation features
function initializeAutomation() {
    console.log('🤖 Initializing TurboX automation...');
    
    // Inject automation utilities
    injectAutomationScript();
    
    // Start observing page changes
    observePageChanges();
    
    // Auto-detect login forms
    detectLoginForms();
    
    // Connect to desktop socket bridge
    connectToDesktop();
}

// Inject automation utilities into page
function injectAutomationScript() {
    const script = document.createElement('script');
    script.src = chrome.runtime.getURL('injected.js');
    script.onload = function() {
        this.remove();
    };
    (document.head || document.documentElement).appendChild(script);
}

// Observe DOM changes for dynamic content
function observePageChanges() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            // Check for new forms
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        if (node.tagName === 'FORM' || node.querySelector?.('form')) {
                            detectLoginForms();
                        }
                        
                        // Check for CAPTCHA elements
                        detectCaptchaElements(node);
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Detect login forms on the page
function detectLoginForms() {
    const forms = document.querySelectorAll('form');
    const loginForms = [];
    
    forms.forEach((form, index) => {
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        const hasCredentials = Array.from(inputs).some(input => 
            ['username', 'email', 'password', 'pass', 'pwd'].some(keyword => 
                input.name.toLowerCase().includes(keyword) || 
                input.id.toLowerCase().includes(keyword) ||
                input.placeholder?.toLowerCase().includes(keyword)
            )
        );
        
        if (hasCredentials) {
            const formData = {
                id: `form_${index}`,
                action: form.action || window.location.href,
                method: form.method || 'GET',
                inputs: Array.from(inputs).map(input => ({
                    name: input.name,
                    type: input.type,
                    id: input.id,
                    placeholder: input.placeholder,
                    value: input.value
                })),
                hasCaptcha: form.querySelector('.g-recaptcha, [class*="captcha"], img[src*="captcha"]') !== null
            };
            
            loginForms.push(formData);
            
            // Highlight login form
            form.style.border = '2px solid #1dd1a1';
            form.style.borderRadius = '5px';
            form.style.padding = '5px';
        }
    });
    
    if (loginForms.length > 0) {
        console.log(`🔍 Found ${loginForms.length} login form(s)`);
        
        // Send to background script
        chrome.runtime.sendMessage({
            type: 'LOGIN_FORMS_DETECTED',
            forms: loginForms
        });
    }
}

// Detect CAPTCHA elements
function detectCaptchaElements(element) {
    // Check for reCAPTCHA
    const recaptcha = element.querySelector?.('.g-recaptcha');
    if (recaptcha) {
        console.log('🔍 Found reCAPTCHA');
        
        chrome.runtime.sendMessage({
            type: 'CAPTCHA_DETECTED',
            captcha: {
                type: 'recaptcha',
                element: 'g-recaptcha'
            }
        });
    }
    
    // Check for image CAPTCHA
    const captchaImages = element.querySelectorAll?.('img[src*="captcha"], img[alt*="CAPTCHA"]');
    captchaImages?.forEach(img => {
        console.log('🔍 Found image CAPTCHA');
        
        // Convert image to base64
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        
        const imageData = canvas.toDataURL('image/png').split(',')[1];
        
        chrome.runtime.sendMessage({
            type: 'CAPTCHA_DETECTED',
            captcha: {
                type: 'image',
                image: imageData,
                src: img.src
            }
        });
    });
    
    // Check for math CAPTCHA
    const mathCaptcha = element.textContent?.match(/(\d+\s*[+\-×*÷/]\s*\d+)/);
    if (mathCaptcha) {
        console.log('🔍 Found math CAPTCHA:', mathCaptcha[0]);
        
        chrome.runtime.sendMessage({
            type: 'CAPTCHA_DETECTED',
            captcha: {
                type: 'math',
                question: mathCaptcha[0]
            }
        });
    }
}

// Connect to desktop socket bridge
function connectToDesktop() {
    const socketUrl = 'ws://localhost:8766'; // Socket bridge WebSocket
    
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    
    function connect() {
        socket = new WebSocket(socketUrl);
        
        socket.onopen = function() {
            console.log('🌐 Connected to TurboX Desktop');
            reconnectAttempts = 0;
            
            // Identify as browser extension
            socket.send(JSON.stringify({
                type: 'identity',
                client: 'browser_extension'
            }));
        };
        
        socket.onmessage = function(event) {
            try {
                const message = JSON.parse(event.data);
                handleDesktopMessage(message);
            } catch (error) {
                console.error('❌ Invalid message from desktop:', error);
            }
        };
        
        socket.onclose = function() {
            console.log('🌐 Disconnected from TurboX Desktop');
            
            // Attempt reconnect
            if (reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                console.log(`🔄 Reconnecting (attempt ${reconnectAttempts})...`);
                setTimeout(connect, 3000);
            }
        };
        
        socket.onerror = function(error) {
            console.error('❌ WebSocket error:', error);
        };
    }
    
    // Initial connection
    connect();
    
    // Periodically check connection
    setInterval(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            // Send heartbeat
            socket.send(JSON.stringify({
                type: 'heartbeat',
                timestamp: Date.now()
            }));
        }
    }, 30000);
}

// Handle messages from desktop
function handleDesktopMessage(message) {
    switch (message.type) {
        case 'launch_tools':
            // Request to launch desktop tools
            console.log('🚀 Launching desktop tools...');
            chrome.runtime.sendMessage({
                type: 'LAUNCH_TOOLS',
                tools: message.tools
            });
            break;
            
        case 'automation_script':
            // Execute automation script
            executeAutomationScript(message.script);
            break;
            
        case 'fill_form':
            // Auto-fill form
            autoFillForm(message.formData);
            break;
            
        case 'solve_captcha':
            // Solve CAPTCHA
            solveCaptcha(message.captchaData);
            break;
            
        case 'export_data':
            // Export captured data
            exportCapturedData(message.format);
            break;
    }
}

// Execute automation script
function executeAutomationScript(script) {
    try {
        // Create a function from the script
        const automationFunction = new Function(script);
        
        // Execute with page context
        automationFunction.call(window);
        
        console.log('✅ Automation script executed');
        
        // Report back to desktop
        chrome.runtime.sendMessage({
            type: 'AUTOMATION_COMPLETED',
            script: script
        });
        
    } catch (error) {
        console.error('❌ Automation script error:', error);
        
        chrome.runtime.sendMessage({
            type: 'AUTOMATION_ERROR',
            error: error.message,
            script: script
        });
    }
}

// Auto-fill form
function autoFillForm(formData) {
    const form = document.querySelector(formData.selector) || 
                 document.forms[formData.formIndex];
    
    if (!form) {
        console.error('❌ Form not found');
        return;
    }
    
    // Fill each field
    Object.entries(formData.fields).forEach(([fieldName, value]) => {
        const input = form.querySelector(`[name="${fieldName}"]`) ||
                     form.querySelector(`#${fieldName}`) ||
                     form.querySelector(`[name*="${fieldName}"]`);
        
        if (input) {
            input.value = value;
            
            // Trigger change event
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
    
    console.log(`✅ Form auto-filled with ${Object.keys(formData.fields).length} fields`);
}

// Solve CAPTCHA
function solveCaptcha(captchaData) {
    const { type, solution } = captchaData;
    
    if (type === 'recaptcha' && window.grecaptcha) {
        // For reCAPTCHA v2
        const recaptchaElement = document.querySelector('.g-recaptcha');
        if (recaptchaElement) {
            const widgetId = recaptchaElement.getAttribute('data-widget-id');
            if (widgetId) {
                window.grecaptcha.execute(widgetId);
            }
        }
    } else if (type === 'image') {
        // Find CAPTCHA input field
        const captchaInput = document.querySelector('input[name="captcha"], input[name="verification"]');
        if (captchaInput) {
            captchaInput.value = solution;
            
            // Trigger events
            captchaInput.dispatchEvent(new Event('input', { bubbles: true }));
            captchaInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    } else if (type === 'math') {
        // Find math CAPTCHA input
        const mathInputs = document.querySelectorAll('input[type="text"], input[type="number"]');
        mathInputs.forEach(input => {
            const label = input.previousElementSibling?.textContent || '';
            if (label.includes('+') || label.includes('-') || label.includes('×') || label.includes('÷')) {
                input.value = solution;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
    }
    
    console.log(`✅ CAPTCHA solved: ${type}`);
}

// Export captured data
function exportCapturedData(format = 'json') {
    chrome.runtime.sendMessage({
        type: 'EXPORT_DATA_REQUEST',
        format: format
    });
}

// Get current page information
function getPageInfo() {
    return {
        url: window.location.href,
        title: document.title,
        domain: window.location.hostname,
        forms: Array.from(document.forms).map((form, index) => ({
            index: index,
            action: form.action,
            method: form.method,
            inputs: Array.from(form.elements).map(el => ({
                name: el.name,
                type: el.type,
                tagName: el.tagName
            }))
        })),
        hasCaptcha: document.querySelector('.g-recaptcha, [class*="captcha"]') !== null,
        timestamp: new Date().toISOString()
    };
}

// Intercept form submissions
document.addEventListener('submit', function(event) {
    if (!isActive) return;
    
    const form = event.target;
    
    // Collect form data
    const formData = new FormData(form);
    const formObject = {};
    
    for (const [key, value] of formData.entries()) {
        formObject[key] = value;
    }
    
    // Send to background script
    chrome.runtime.sendMessage({
        type: 'FORM_SUBMISSION',
        form: {
            action: form.action,
            method: form.method,
            data: formObject
        },
        url: window.location.href
    });
    
    console.log(`📝 Form submitted: ${form.action}`);
}, true);

// Intercept AJAX requests
if (window.XMLHttpRequest) {
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;
    
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        this._turboXMethod = method;
        this._turboXUrl = url;
        
        return originalOpen.apply(this, arguments);
    };
    
    XMLHttpRequest.prototype.send = function(body) {
        if (isCapturing) {
            const startTime = Date.now();
            
            this.addEventListener('load', function() {
                const requestData = {
                    type: 'xhr',
                    method: this._turboXMethod,
                    url: this._turboXUrl,
                    status: this.status,
                    response: this.response,
                    responseText: this.responseText,
                    responseType: this.responseType,
                    responseURL: this.responseURL,
                    duration: Date.now() - startTime,
                    timestamp: new Date().toISOString()
                };
                
                capturedRequests.push(requestData);
                
                // Send to background script
                chrome.runtime.sendMessage({
                    type: 'XHR_CAPTURED',
                    request: requestData
                });
            });
        }
        
        return originalSend.apply(this, arguments);
    };
}

// Intercept fetch requests
if (window.fetch) {
    const originalFetch = window.fetch;
    
    window.fetch = function(input, init) {
        const startTime = Date.now();
        
        if (isCapturing) {
            const method = (init?.method || 'GET').toUpperCase();
            const url = typeof input === 'string' ? input : input.url;
            
            return originalFetch.apply(this, arguments).then(response => {
                response.clone().text().then(responseText => {
                    const requestData = {
                        type: 'fetch',
                        method: method,
                        url: url,
                        status: response.status,
                        statusText: response.statusText,
                        response: responseText,
                        duration: Date.now() - startTime,
                        timestamp: new Date().toISOString()
                    };
                    
                    capturedRequests.push(requestData);
                    
                    chrome.runtime.sendMessage({
                        type: 'FETCH_CAPTURED',
                        request: requestData
                    });
                });
                
                return response;
            });
        }
        
        return originalFetch.apply(this, arguments);
    };
}

// Send periodic updates to background script
setInterval(() => {
    if (isActive && capturedRequests.length > 0) {
        // Send batch of captured requests
        const batch = capturedRequests.splice(0, 50); // Send in batches
        
        chrome.runtime.sendMessage({
            type: 'CAPTURED_REQUESTS_BATCH',
            requests: batch
        });
    }
}, 5000); // Send every 5 seconds

console.log('✅ TurboX content script loaded');
