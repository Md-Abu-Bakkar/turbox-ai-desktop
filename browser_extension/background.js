// TurboX DevTools Pro - Background Service Worker
// Phase 2: Core Network Interception

// Global state
let interceptedRequests = new Map();
let activeSessions = new Map();
let isCapturing = false;
let apiTesterEnabled = false;
let smsPanelEnabled = false;

// Listen for installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('✅ TurboX DevTools Pro installed');
  initializeStorage();
});

// Initialize storage
function initializeStorage() {
  chrome.storage.local.get(['turboXConfig'], (result) => {
    if (!result.turboXConfig) {
      const defaultConfig = {
        apiTester: {
          enabled: false,
          autoCapture: true,
          saveRequests: true
        },
        smsPanel: {
          enabled: false,
          autoDetectSMS: true
        },
        devTools: {
          captureNetwork: true,
          captureDOM: false,
          captureConsole: false
        },
        captcha: {
          autoSolve: false,
          service: 'none'
        }
      };
      chrome.storage.local.set({ turboXConfig: defaultConfig });
    }
  });
}

// Network request interception
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    if (!isCapturing) return;
    
    const requestId = details.requestId;
    const requestData = {
      id: requestId,
      url: details.url,
      method: details.method,
      type: details.type,
      tabId: details.tabId,
      timestamp: Date.now(),
      requestBody: null,
      status: 'pending'
    };
    
    // Store request
    interceptedRequests.set(requestId, requestData);
    
    // Notify content script
    chrome.tabs.sendMessage(details.tabId, {
      type: 'REQUEST_STARTED',
      data: requestData
    }).catch(() => {});
    
    // Send to API Tester if enabled
    if (apiTesterEnabled) {
      sendToAPITester('request_started', requestData);
    }
  },
  { urls: ["<all_urls>"] },
  ["requestBody"]
);

// Response interception
chrome.webRequest.onCompleted.addListener(
  (details) => {
    if (!isCapturing) return;
    
    const requestId = details.requestId;
    const requestData = interceptedRequests.get(requestId);
    
    if (requestData) {
      requestData.status = 'completed';
      requestData.statusCode = details.statusCode;
      requestData.responseHeaders = details.responseHeaders;
      requestData.completedTime = Date.now();
      
      // Get response body
      chrome.debugger.getTargets((targets) => {
        const target = targets.find(t => t.tabId === details.tabId);
        if (target) {
          attachDebugger(target, details);
        }
      });
      
      // Check for SMS data if SMS panel enabled
      if (smsPanelEnabled && isSMSRequest(details.url)) {
        processSMSData(requestData);
      }
      
      // Notify content script
      chrome.tabs.sendMessage(details.tabId, {
        type: 'REQUEST_COMPLETED',
        data: requestData
      }).catch(() => {});
      
      // Send to API Tester
      if (apiTesterEnabled) {
        sendToAPITester('request_completed', requestData);
      }
    }
  },
  { urls: ["<all_urls>"] },
  ["responseHeaders"]
);

// Error handling
chrome.webRequest.onErrorOccurred.addListener(
  (details) => {
    if (!isCapturing) return;
    
    const requestId = details.requestId;
    const requestData = interceptedRequests.get(requestId);
    
    if (requestData) {
      requestData.status = 'error';
      requestData.error = details.error;
      requestData.completedTime = Date.now();
      
      // Notify content script
      chrome.tabs.sendMessage(details.tabId, {
        type: 'REQUEST_ERROR',
        data: requestData
      }).catch(() => {});
    }
  },
  { urls: ["<all_urls>"] }
);

// Debugger attachment for response body
function attachDebugger(target, details) {
  const debuggee = { targetId: target.id };
  
  chrome.debugger.attach(debuggee, "1.3", () => {
    if (chrome.runtime.lastError) return;
    
    chrome.debugger.sendCommand(debuggee, "Network.getResponseBody", {
      requestId: details.requestId
    }, (response) => {
      if (response) {
        const requestData = interceptedRequests.get(details.requestId);
        if (requestData) {
          requestData.responseBody = response.body;
          requestData.base64Encoded = response.base64Encoded;
          
          // Save to storage
          saveRequestToStorage(requestData);
        }
      }
      chrome.debugger.detach(debuggee);
    });
  });
}

// SMS data detection and processing
function isSMSRequest(url) {
  const smsKeywords = [
    'sms', 'message', 'text', 'mms', 'twilio',
    'nexmo', 'plivo', 'messagebird', 'bulksms'
  ];
  return smsKeywords.some(keyword => 
    url.toLowerCase().includes(keyword)
  );
}

function processSMSData(requestData) {
  try {
    let smsData = null;
    
    if (requestData.responseBody) {
      // Try to parse as JSON
      if (!requestData.base64Encoded) {
        try {
          const parsed = JSON.parse(requestData.responseBody);
          if (parsed.messages || parsed.sms || parsed.texts) {
            smsData = extractSMSFromJSON(parsed);
          }
        } catch (e) {
          // Not JSON, try other formats
          smsData = extractSMSFromText(requestData.responseBody);
        }
      }
    }
    
    if (smsData) {
      // Send to SMS Panel
      sendToSMSPanel(smsData);
      
      // Save to storage
      chrome.storage.local.get(['smsMessages'], (result) => {
        const messages = result.smsMessages || [];
        messages.push({
          ...smsData,
          source: requestData.url,
          timestamp: new Date().toISOString()
        });
        chrome.storage.local.set({ smsMessages: messages });
      });
    }
  } catch (error) {
    console.error('SMS processing error:', error);
  }
}

function extractSMSFromJSON(data) {
  // Extract SMS data from common API formats
  const smsData = {
    messages: [],
    count: 0,
    metadata: {}
  };
  
  if (Array.isArray(data)) {
    smsData.messages = data.map(msg => ({
      id: msg.id || msg.message_id,
      from: msg.from || msg.sender,
      to: msg.to || msg.recipient,
      body: msg.body || msg.text || msg.message,
      timestamp: msg.timestamp || msg.date,
      status: msg.status
    }));
  } else if (data.messages && Array.isArray(data.messages)) {
    smsData.messages = data.messages;
  } else if (data.sms && Array.isArray(data.sms)) {
    smsData.messages = data.sms;
  }
  
  smsData.count = smsData.messages.length;
  return smsData;
}

function extractSMSFromText(text) {
  // Basic SMS extraction from text/XML responses
  const smsData = {
    messages: [],
    count: 0,
    metadata: { format: 'text' }
  };
  
  // Simple regex for phone numbers and messages
  const phoneRegex = /(\+\d{10,15})|(\d{10,15})/g;
  const messageRegex = /body="([^"]+)"|text="([^"]+)"|message="([^"]+)"/gi;
  
  const phones = text.match(phoneRegex) || [];
  const messages = [];
  
  let match;
  while ((match = messageRegex.exec(text)) !== null) {
    messages.push(match[1] || match[2] || match[3]);
  }
  
  // Create simple message objects
  for (let i = 0; i < Math.min(phones.length, messages.length); i++) {
    smsData.messages.push({
      id: `sms_${i}`,
      from: phones[i] || 'Unknown',
      body: messages[i],
      timestamp: new Date().toISOString()
    });
  }
  
  smsData.count = smsData.messages.length;
  return smsData;
}

// Communication with API Tester desktop app
function sendToAPITester(event, data) {
  // This will connect to local socket in Phase 3
  console.log(`📤 To API Tester [${event}]:`, data.url);
  
  // Store for desktop app pickup
  chrome.storage.local.get(['apiRequests'], (result) => {
    const requests = result.apiRequests || [];
    requests.push({
      event,
      data,
      timestamp: Date.now()
    });
    
    // Keep only last 1000 requests
    if (requests.length > 1000) {
      requests.splice(0, requests.length - 1000);
    }
    
    chrome.storage.local.set({ apiRequests: requests });
  });
}

function sendToSMSPanel(smsData) {
  console.log(`📱 To SMS Panel: ${smsData.count} messages`);
  
  chrome.storage.local.get(['smsPanelData'], (result) => {
    const panelData = result.smsPanelData || { messages: [], stats: {} };
    panelData.messages.push(...smsData.messages);
    panelData.stats.total = panelData.messages.length;
    panelData.stats.lastUpdate = new Date().toISOString();
    
    chrome.storage.local.set({ smsPanelData: panelData });
  });
}

function saveRequestToStorage(requestData) {
  chrome.storage.local.get(['capturedRequests'], (result) => {
    const requests = result.capturedRequests || [];
    requests.push(requestData);
    
    // Limit storage
    if (requests.length > 500) {
      requests.splice(0, requests.length - 500);
    }
    
    chrome.storage.local.set({ capturedRequests: requests });
  });
}

// Message handling from popup/content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case 'TOGGLE_CAPTURE':
      isCapturing = message.enabled;
      sendResponse({ success: true, capturing: isCapturing });
      break;
      
    case 'TOGGLE_API_TESTER':
      apiTesterEnabled = message.enabled;
      sendResponse({ success: true, enabled: apiTesterEnabled });
      break;
      
    case 'TOGGLE_SMS_PANEL':
      smsPanelEnabled = message.enabled;
      sendResponse({ success: true, enabled: smsPanelEnabled });
      break;
      
    case 'GET_CAPTURED_DATA':
      chrome.storage.local.get(['capturedRequests', 'smsPanelData'], (result) => {
        sendResponse({
          requests: result.capturedRequests || [],
          smsData: result.smsPanelData || { messages: [], stats: {} }
        });
      });
      return true; // Async response
      
    case 'CLEAR_DATA':
      interceptedRequests.clear();
      chrome.storage.local.remove(['capturedRequests', 'smsPanelData', 'apiRequests']);
      sendResponse({ success: true });
      break;
      
    case 'EXPORT_DATA':
      exportData(message.format).then(data => {
        sendResponse({ success: true, data });
      });
      return true;
      
    default:
      sendResponse({ error: 'Unknown message type' });
  }
});

async function exportData(format = 'json') {
  return new Promise((resolve) => {
    chrome.storage.local.get(['capturedRequests', 'smsPanelData', 'apiRequests'], (result) => {
      const exportData = {
        metadata: {
          exportDate: new Date().toISOString(),
          tool: 'TurboX DevTools Pro',
          version: '1.0'
        },
        networkRequests: result.capturedRequests || [],
        smsData: result.smsPanelData || { messages: [], stats: {} },
        apiRequests: result.apiRequests || []
      };
      
      if (format === 'json') {
        resolve(JSON.stringify(exportData, null, 2));
      } else if (format === 'csv') {
        resolve(convertToCSV(exportData));
      } else {
        resolve(exportData);
      }
    });
  });
}

function convertToCSV(data) {
  // Simplified CSV conversion
  let csv = 'Type,URL,Method,Status,Timestamp\n';
  
  data.networkRequests.forEach(req => {
    csv += `Request,${req.url},${req.method},${req.statusCode || 'pending'},${new Date(req.timestamp).toLocaleString()}\n`;
  });
  
  data.smsData.messages.forEach((msg, i) => {
    csv += `SMS,Message ${i + 1},${msg.from || 'Unknown'},${msg.to || 'Unknown'},${msg.timestamp}\n`;
  });
  
  return csv;
}

// Session management
class SessionManager {
  constructor() {
    this.sessions = new Map();
  }
  
  createSession(domain, credentials) {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const session = {
      id: sessionId,
      domain,
      credentials,
      tokens: {},
      cookies: [],
      createdAt: new Date().toISOString(),
      lastUsed: new Date().toISOString()
    };
    
    this.sessions.set(sessionId, session);
    this.saveSessions();
    return sessionId;
  }
  
  updateTokens(sessionId, tokens) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.tokens = { ...session.tokens, ...tokens };
      session.lastUsed = new Date().toISOString();
      this.saveSessions();
    }
  }
  
  getSessionForDomain(domain) {
    for (const [id, session] of this.sessions) {
      if (session.domain.includes(domain) || domain.includes(session.domain)) {
        session.lastUsed = new Date().toISOString();
        return session;
      }
    }
    return null;
  }
  
  saveSessions() {
    const sessionsArray = Array.from(this.sessions.entries()).map(([id, session]) => ({
      id,
      ...session
    }));
    
    chrome.storage.local.set({ turboXSessions: sessionsArray });
  }
  
  loadSessions() {
    chrome.storage.local.get(['turboXSessions'], (result) => {
      if (result.turboXSessions) {
        result.turboXSessions.forEach(session => {
          this.sessions.set(session.id, session);
        });
      }
    });
  }
}

const sessionManager = new SessionManager();
sessionManager.loadSessions();
