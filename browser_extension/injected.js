// TurboX DevTools Pro - Injected Script
// Runs in page context for automation

(function() {
    'use strict';
    
    // Create TurboX namespace in page context
    window.TurboX = window.TurboX || {
        version: '1.0',
        automation: {},
        utils: {}
    };
    
    // Utility functions
    TurboX.utils = {
        // Wait for element to appear
        waitForElement: function(selector, timeout = 10000) {
            return new Promise((resolve, reject) => {
                const startTime = Date.now();
                
                function check() {
                    const element = document.querySelector(selector);
                    if (element) {
                        resolve(element);
                    } else if (Date.now() - startTime > timeout) {
                        reject(new Error(`Element not found: ${selector}`));
                    } else {
                        setTimeout(check, 100);
                    }
                }
                
                check();
            });
        },
        
        // Wait for function to return true
        waitForCondition: function(conditionFn, timeout = 10000) {
            return new Promise((resolve, reject) => {
                const startTime = Date.now();
                
                function check() {
                    try {
                        if (conditionFn()) {
                            resolve(true);
                        } else if (Date.now() - startTime > timeout) {
                            reject(new Error('Condition timeout'));
                        } else {
                            setTimeout(check, 100);
                        }
                    } catch (error) {
                        reject(error);
                    }
                }
                
                check();
            });
        },
        
        // Fill form fields
        fillForm: function(formSelector, data) {
            const form = document.querySelector(formSelector);
            if (!form) return false;
            
            Object.entries(data).forEach(([field, value]) => {
                const input = form.querySelector(`[name="${field}"]`) ||
                             form.querySelector(`#${field}`);
                
                if (input) {
                    input.value = value;
                    
                    // Trigger events
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
            
            return true;
        },
        
        // Submit form
        submitForm: function(formSelector) {
            const form = document.querySelector(formSelector);
            if (form) {
                form.submit();
                return true;
            }
            return false;
        },
        
        // Click element
        clickElement: function(selector) {
            const element = document.querySelector(selector);
            if (element) {
                element.click();
                return true;
            }
            return false;
        },
        
        // Get page data
        getPageData: function() {
            return {
                url: window.location.href,
                title: document.title,
                forms: Array.from(document.forms).map(form => ({
                    action: form.action,
                    method: form.method,
                    elements: Array.from(form.elements).map(el => ({
                        name: el.name,
                        type: el.type,
                        tagName: el.tagName,
                        value: el.value
                    }))
                })),
                links: Array.from(document.links).map(link => ({
                    href: link.href,
                    text: link.textContent
                }))
            };
        },
        
        // Extract data from tables
        extractTableData: function(tableSelector) {
            const table = document.querySelector(tableSelector);
            if (!table) return [];
            
            const rows = table.querySelectorAll('tr');
            const data = [];
            
            // Get headers
            const headers = Array.from(rows[0].querySelectorAll('th, td')).map(cell => 
                cell.textContent.trim()
            );
            
            // Get rows
            for (let i = 1; i < rows.length; i++) {
                const cells = rows[i].querySelectorAll('td');
                const rowData = {};
                
                cells.forEach((cell, index) => {
                    const header = headers[index] || `column_${index}`;
                    rowData[header] = cell.textContent.trim();
                });
                
                data.push(rowData);
            }
            
            return data;
        },
        
        // Monitor element changes
        observeElement: function(selector, callback) {
            const element = document.querySelector(selector);
            if (!element) return null;
            
            const observer = new MutationObserver((mutations) => {
                callback(mutations, element);
            });
            
            observer.observe(element, {
                childList: true,
                subtree: true,
                characterData: true,
                attributes: true
            });
            
            return observer;
        }
    };
    
    // Automation functions
    TurboX.automation = {
        // Auto-login
        autoLogin: function(credentials) {
            return new Promise((resolve, reject) => {
                try {
                    // Find login form
                    const forms = document.querySelectorAll('form');
                    let loginForm = null;
                    
                    for (const form of forms) {
                        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
                        const hasLoginFields = Array.from(inputs).some(input => 
                            ['username', 'email', 'password', 'pass', 'pwd'].some(keyword => 
                                input.name.toLowerCase().includes(keyword)
                            )
                        );
                        
                        if (hasLoginFields) {
                            loginForm = form;
                            break;
                        }
                    }
                    
                    if (!loginForm) {
                        reject(new Error('No login form found'));
                        return;
                    }
                    
                    // Fill credentials
                    Object.entries(credentials).forEach(([field, value]) => {
                        const input = loginForm.querySelector(`[name*="${field}"]`) ||
                                     loginForm.querySelector(`[name*="${field.toLowerCase()}"]`);
                        
                        if (input) {
                            input.value = value;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    });
                    
                    // Check for CAPTCHA
                    const captcha = loginForm.querySelector('.g-recaptcha, [class*="captcha"]');
                    if (captcha) {
                        console.log('⚠️ CAPTCHA detected, manual solving required');
                        // CAPTCHA will be handled by background script
                    }
                    
                    // Submit form
                    loginForm.submit();
                    
                    resolve({
                        success: true,
                        message: 'Login form submitted'
                    });
                    
                } catch (error) {
                    reject(error);
                }
            });
        },
        
        // Auto-fill forms
        autoFillForms: function(data) {
            const forms = document.querySelectorAll('form');
            
            forms.forEach(form => {
                Object.entries(data).forEach(([field, value]) => {
                    const input = form.querySelector(`[name="${field}"]`) ||
                                 form.querySelector(`[name*="${field}"]`);
                    
                    if (input && !input.value) {
                        input.value = value;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            });
            
            return forms.length;
        },
        
        // Extract data from page
        extractData: function(config) {
            const results = {};
            
            if (config.tables) {
                config.tables.forEach(tableConfig => {
                    results[tableConfig.name] = TurboX.utils.extractTableData(tableConfig.selector);
                });
            }
            
            if (config.elements) {
                config.elements.forEach(elementConfig => {
                    const elements = document.querySelectorAll(elementConfig.selector);
                    results[elementConfig.name] = Array.from(elements).map(el => 
                        elementConfig.attribute ? el.getAttribute(elementConfig.attribute) : el.textContent.trim()
                    );
                });
            }
            
            return results;
        },
        
        // Navigate to URL
        navigate: function(url) {
            window.location.href = url;
        },
        
        // Click buttons/links
        click: function(selector) {
            const element = document.querySelector(selector);
            if (element) {
                element.click();
                return true;
            }
            return false;
        },
        
        // Scroll to element
        scrollTo: function(selector) {
            const element = document.querySelector(selector);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
                return true;
            }
            return false;
        },
        
        // Monitor page for changes
        monitorPage: function(callback) {
            const observer = new MutationObserver((mutations) => {
                callback(mutations);
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            return observer;
        },
        
        // Get all API endpoints from page
        getApiEndpoints: function() {
            const endpoints = new Set();
            
            // Check script tags for API URLs
            const scripts = document.querySelectorAll('script');
            scripts.forEach(script => {
                const content = script.textContent;
                const urlRegex = /(https?:\/\/[^"'\s]+?\/api\/[^"'\s]+)/g;
                const matches = content.match(urlRegex);
                if (matches) {
                    matches.forEach(match => endpoints.add(match));
                }
            });
            
            // Check for fetch/XHR in page code (simplified)
            const allCode = document.documentElement.outerHTML;
            const apiPatterns = [
                /fetch\(['"]([^'"]+?)['"]/g,
                /\.ajax\(['"]([^'"]+?)['"]/g,
                /axios\.(get|post|put|delete)\(['"]([^'"]+?)['"]/g,
                /XMLHttpRequest\(\)\.open\(['"](GET|POST|PUT|DELETE)['"]['"]([^'"]+?)['"]/g
            ];
            
            apiPatterns.forEach(pattern => {
                let match;
                while ((match = pattern.exec(allCode)) !== null) {
                    const url = match[2] || match[1];
                    if (url && url.includes('/api/')) {
                        endpoints.add(url);
                    }
                }
            });
            
            return Array.from(endpoints);
        }
    };
    
    // Communication with content script
    function sendToContentScript(message) {
        window.postMessage({
            type: 'TURBOX_MESSAGE',
            data: message
        }, '*');
    }
    
    // Listen for messages from content script
    window.addEventListener('message', function(event) {
        if (event.source !== window) return;
        if (event.data.type !== 'TURBOX_COMMAND') return;
        
        const command = event.data.command;
        const data = event.data.data;
        
        // Execute command
        switch (command) {
            case 'EXECUTE_AUTOMATION':
                try {
                    const result = TurboX.automation[data.function](...data.args);
                    sendToContentScript({
                        type: 'AUTOMATION_RESULT',
                        result: result
                    });
                } catch (error) {
                    sendToContentScript({
                        type: 'AUTOMATION_ERROR',
                        error: error.message
                    });
                }
                break;
                
            case 'GET_PAGE_DATA':
                const pageData = TurboX.utils.getPageData();
                sendToContentScript({
                    type: 'PAGE_DATA',
                    data: pageData
                });
                break;
                
            case 'EXTRACT_DATA':
                const extracted = TurboX.automation.extractData(data.config);
                sendToContentScript({
                    type: 'EXTRACTED_DATA',
                    data: extracted
                });
                break;
        }
    });
    
    // Notify that TurboX is loaded
    sendToContentScript({
        type: 'TURBOX_LOADED',
        version: TurboX.version
    });
    
    console.log('✅ TurboX automation injected');
    
})();
