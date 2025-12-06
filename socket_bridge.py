#!/data/data/com.termux/files/usr/bin/python3
# ==============================================================================
# TurboX Desktop OS - Socket Bridge
# Phase 3: Real-time Desktop-Browser Communication
# ==============================================================================

import os
import sys
import json
import socket
import threading
import time
import queue
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class SocketBridge:
    """Bridge between desktop applications and browser extension"""
    
    def __init__(self, port=8765):
        self.port = port
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        self.data_dir = os.path.join(self.config_dir, 'data')
        
        # Ensure directories
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Communication queues
        self.browser_to_desktop = queue.Queue()
        self.desktop_to_browser = queue.Queue()
        
        # Connected clients
        self.clients = {}
        self.browser_connected = False
        
        # Session management
        self.sessions = {}
        self.active_tools = {
            'api_tester': False,
            'sms_panel': False,
            'dev_tools': False
        }
        
        # Start servers
        self.start_http_server()
        self.start_websocket_server()
        
        print(f"✅ Socket Bridge started on port {self.port}")
        print(f"   HTTP: http://localhost:{self.port}")
        print(f"   WebSocket: ws://localhost:{self.port}/ws")
    
    def start_http_server(self):
        """Start HTTP server for browser extension communication"""
        class BridgeHandler(BaseHTTPRequestHandler):
            bridge = self
            
            def do_GET(self):
                parsed = urlparse(self.path)
                
                if parsed.path == '/status':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    status = {
                        'status': 'active',
                        'tools': self.bridge.active_tools,
                        'sessions': len(self.bridge.sessions),
                        'timestamp': datetime.now().isoformat()
                    }
                    self.wfile.write(json.dumps(status).encode())
                
                elif parsed.path == '/data':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    # Get data for browser
                    data = self.bridge.get_data_for_browser()
                    self.wfile.write(json.dumps(data).encode())
                
                elif parsed.path.startswith('/launch/'):
                    tool = parsed.path.split('/')[2]
                    success = self.bridge.launch_tool(tool)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {'success': success, 'tool': tool}
                    self.wfile.write(json.dumps(response).encode())
                
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                try:
                    data = json.loads(post_data.decode())
                    parsed = urlparse(self.path)
                    
                    if parsed.path == '/capture':
                        # Browser sending captured data
                        self.bridge.process_browser_data(data)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        response = {'received': True, 'count': len(data.get('requests', []))}
                        self.wfile.write(json.dumps(response).encode())
                    
                    elif parsed.path == '/session':
                        # Update session data
                        session_id = data.get('session_id')
                        if session_id:
                            self.bridge.update_session(session_id, data)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({'success': True}).encode())
                    
                    elif parsed.path == '/captcha':
                        # CAPTCHA solving request
                        captcha_data = data.get('captcha')
                        solution = self.bridge.solve_captcha(captcha_data)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({'solution': solution}).encode())
                    
                    else:
                        self.send_response(404)
                        self.end_headers()
                        
                except Exception as e:
                    print(f"❌ POST error: {e}")
                    self.send_response(500)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress log messages
        
        # Start HTTP server in thread
        server = HTTPServer(('localhost', self.port), BridgeHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        self.http_server = server
    
    def start_websocket_server(self):
        """Start WebSocket server for real-time communication"""
        # Simplified WebSocket-like communication using threading
        self.ws_running = True
        self.ws_thread = threading.Thread(target=self._websocket_handler, daemon=True)
        self.ws_thread.start()
    
    def _websocket_handler(self):
        """Handle WebSocket-like connections"""
        import select
        
        # Create TCP socket
        ws_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ws_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ws_socket.bind(('localhost', self.port + 1))
        ws_socket.listen(5)
        
        print(f"📡 WebSocket server on port {self.port + 1}")
        
        while self.ws_running:
            try:
                readable, _, _ = select.select([ws_socket], [], [], 1)
                
                if readable:
                    client_socket, addr = ws_socket.accept()
                    client_id = f"{addr[0]}:{addr[1]}"
                    
                    # Handle client in new thread
                    client_thread = threading.Thread(
                        target=self._handle_ws_client,
                        args=(client_socket, client_id),
                        daemon=True
                    )
                    client_thread.start()
                    
            except Exception as e:
                print(f"⚠️ WebSocket error: {e}")
                time.sleep(1)
        
        ws_socket.close()
    
    def _handle_ws_client(self, client_socket, client_id):
        """Handle WebSocket client connection"""
        try:
            self.clients[client_id] = {
                'socket': client_socket,
                'connected_at': datetime.now().isoformat(),
                'type': 'unknown'
            }
            
            # Identify client type
            data = client_socket.recv(1024).decode()
            if data:
                try:
                    msg = json.loads(data)
                    client_type = msg.get('type', 'unknown')
                    self.clients[client_id]['type'] = client_type
                    
                    if client_type == 'browser':
                        self.browser_connected = True
                        print(f"🌐 Browser connected: {client_id}")
                    
                    elif client_type in ['api_tester', 'sms_panel']:
                        self.active_tools[client_type] = True
                        print(f"🛠️ {client_type.replace('_', ' ').title()} connected: {client_id}")
                
                except json.JSONDecodeError:
                    pass
            
            # Main client loop
            while client_id in self.clients:
                try:
                    # Check for incoming data
                    client_socket.settimeout(0.5)
                    try:
                        data = client_socket.recv(4096)
                        if data:
                            self._process_client_message(client_id, data.decode())
                    except socket.timeout:
                        pass
                    
                    # Send queued messages to this client
                    if not self.desktop_to_browser.empty():
                        message = self.desktop_to_browser.get_nowait()
                        if message.get('target') == client_type or message.get('target') == 'all':
                            client_socket.send(json.dumps(message).encode())
                    
                    time.sleep(0.1)
                    
                except (ConnectionResetError, BrokenPipeError):
                    break
                except Exception as e:
                    print(f"⚠️ Client {client_id} error: {e}")
                    time.sleep(1)
        
        except Exception as e:
            print(f"❌ Client handler error: {e}")
        
        finally:
            # Cleanup
            if client_id in self.clients:
                client_type = self.clients[client_id].get('type')
                if client_type == 'browser':
                    self.browser_connected = False
                elif client_type in self.active_tools:
                    self.active_tools[client_type] = False
                
                del self.clients[client_id]
            
            try:
                client_socket.close()
            except:
                pass
            
            print(f"📤 Client disconnected: {client_id}")
    
    def _process_client_message(self, client_id, message):
        """Process message from client"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'capture_data':
                # Browser sending captured network data
                requests = data.get('requests', [])
                self._process_captured_requests(requests)
                
                # Forward to tools if they're active
                if self.active_tools['api_tester']:
                    self.desktop_to_browser.put({
                        'type': 'api_requests',
                        'data': requests,
                        'target': 'api_tester',
                        'timestamp': datetime.now().isoformat()
                    })
                
                if self.active_tools['sms_panel']:
                    sms_data = self._extract_sms_from_requests(requests)
                    if sms_data:
                        self.desktop_to_browser.put({
                            'type': 'sms_data',
                            'data': sms_data,
                            'target': 'sms_panel',
                            'timestamp': datetime.now().isoformat()
                        })
            
            elif msg_type == 'tool_status':
                # Tool reporting its status
                tool = data.get('tool')
                status = data.get('status')
                if tool in self.active_tools:
                    self.active_tools[tool] = (status == 'active')
            
            elif msg_type == 'launch_request':
                # Request to launch a tool
                tool = data.get('tool')
                self.launch_tool(tool)
            
            elif msg_type == 'export_request':
                # Export data request
                tool = data.get('tool')
                format = data.get('format', 'json')
                self.export_tool_data(tool, format)
            
            elif msg_type == 'captcha_request':
                # CAPTCHA solving request
                captcha_data = data.get('captcha')
                solution = self.solve_captcha(captcha_data)
                
                # Send solution back
                self.desktop_to_browser.put({
                    'type': 'captcha_solution',
                    'solution': solution,
                    'target': 'browser',
                    'timestamp': datetime.now().isoformat()
                })
        
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON from {client_id}: {message[:100]}")
        except Exception as e:
            print(f"❌ Message processing error: {e}")
    
    def _process_captured_requests(self, requests):
        """Process captured network requests"""
        for req in requests:
            # Save request to file
            self._save_captured_request(req)
            
            # Extract session tokens
            self._extract_tokens(req)
            
            # Check for login forms
            if self._is_login_request(req):
                self._process_login_request(req)
    
    def _save_captured_request(self, request):
        """Save captured request to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"request_{timestamp}_{hash(str(request)) % 10000}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(request, f, indent=2)
        
        except Exception as e:
            print(f"❌ Save request error: {e}")
    
    def _extract_tokens(self, request):
        """Extract tokens from request/response"""
        try:
            # Check response headers for tokens
            response_headers = request.get('responseHeaders', {})
            cookies = response_headers.get('set-cookie', '')
            
            if cookies:
                # Simple cookie parsing
                for cookie in cookies.split(';'):
                    if '=' in cookie:
                        key, value = cookie.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if any(token in key.lower() for token in ['session', 'token', 'auth', 'jwt', 'bearer']):
                            domain = request.get('url', '').split('/')[2]
                            
                            if domain not in self.sessions:
                                self.sessions[domain] = {}
                            
                            self.sessions[domain]['cookies'] = self.sessions[domain].get('cookies', {})
                            self.sessions[domain]['cookies'][key] = value
            
            # Check response body for tokens
            response_body = request.get('responseBody', '')
            if response_body:
                try:
                    body_json = json.loads(response_body)
                    if isinstance(body_json, dict):
                        for key, value in body_json.items():
                            if any(token in key.lower() for token in ['token', 'access', 'refresh', 'auth']):
                                if isinstance(value, str) and len(value) > 10:
                                    domain = request.get('url', '').split('/')[2]
                                    
                                    if domain not in self.sessions:
                                        self.sessions[domain] = {}
                                    
                                    self.sessions[domain]['tokens'] = self.sessions[domain].get('tokens', {})
                                    self.sessions[domain]['tokens'][key] = value
                except:
                    pass
        
        except Exception as e:
            print(f"⚠️ Token extraction error: {e}")
    
    def _is_login_request(self, request):
        """Check if request is a login attempt"""
        url = request.get('url', '').lower()
        method = request.get('method', '').upper()
        
        login_indicators = ['login', 'signin', 'auth', 'authenticate', 'password']
        
        # Check URL
        if any(indicator in url for indicator in login_indicators):
            return True
        
        # Check request body for credentials
        request_body = request.get('requestBody', '').lower()
        if any(field in request_body for field in ['password', 'passwd', 'pwd', 'username', 'email']):
            return True
        
        return False
    
    def _process_login_request(self, request):
        """Process login request for automation"""
        try:
            domain = request.get('url', '').split('/')[2]
            
            if domain not in self.sessions:
                self.sessions[domain] = {
                    'login_url': request.get('url'),
                    'login_method': request.get('method'),
                    'login_headers': request.get('requestHeaders', {}),
                    'login_body': request.get('requestBody', ''),
                    'last_login': datetime.now().isoformat()
                }
            
            # Save login template for future automation
            login_file = os.path.join(self.data_dir, f"login_{domain.replace('.', '_')}.json")
            with open(login_file, 'w') as f:
                json.dump(self.sessions[domain], f, indent=2)
            
            print(f"🔐 Login template saved for {domain}")
        
        except Exception as e:
            print(f"❌ Login processing error: {e}")
    
    def _extract_sms_from_requests(self, requests):
        """Extract SMS data from captured requests"""
        sms_data = []
        
        for req in requests:
            url = req.get('url', '').lower()
            
            # Check if this looks like an SMS API
            sms_indicators = ['sms', 'message', 'text', 'mms', 'twilio', 'nexmo', 'plivo']
            
            if any(indicator in url for indicator in sms_indicators):
                try:
                    # Try to parse response
                    response_body = req.get('responseBody', '')
                    if response_body:
                        response_json = json.loads(response_body)
                        
                        if isinstance(response_json, dict):
                            # Common SMS API formats
                            if 'messages' in response_json:
                                messages = response_json['messages']
                            elif 'sms' in response_json:
                                messages = response_json['sms']
                            elif isinstance(response_json, list):
                                messages = response_json
                            else:
                                messages = []
                            
                            for msg in messages if isinstance(messages, list) else []:
                                sms_data.append({
                                    'id': msg.get('id', msg.get('message_id', '')),
                                    'from': msg.get('from', msg.get('sender', '')),
                                    'to': msg.get('to', msg.get('recipient', '')),
                                    'body': msg.get('body', msg.get('text', msg.get('message', ''))),
                                    'timestamp': msg.get('timestamp', msg.get('date', datetime.now().isoformat())),
                                    'status': msg.get('status', 'unknown'),
                                    'source': req.get('url')
                                })
                
                except Exception as e:
                    print(f"⚠️ SMS extraction error: {e}")
        
        return sms_data
    
    def process_browser_data(self, data):
        """Process data from browser extension"""
        requests = data.get('requests', [])
        if requests:
            self._process_captured_requests(requests)
            
            # Notify tools
            self.browser_to_desktop.put({
                'type': 'new_captures',
                'count': len(requests),
                'timestamp': datetime.now().isoformat()
            })
    
    def update_session(self, session_id, data):
        """Update session data"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        
        self.sessions[session_id].update(data)
        self.sessions[session_id]['last_updated'] = datetime.now().isoformat()
    
    def solve_captcha(self, captcha_data):
        """Solve CAPTCHA (Phase 3 placeholder)"""
        # This will be integrated with external CAPTCHA solving service
        captcha_type = captcha_data.get('type', 'unknown')
        
        if captcha_type == 'image':
            # Save image for manual solving or external API
            image_data = captcha_data.get('image')
            if image_data:
                # Save to file
                import base64
                try:
                    image_bytes = base64.b64decode(image_data)
                    captcha_file = os.path.join(self.data_dir, f"captcha_{int(time.time())}.png")
                    with open(captcha_file, 'wb') as f:
                        f.write(image_bytes)
                    
                    print(f"📸 CAPTCHA saved to: {captcha_file}")
                    return f"MANUAL_SOLVE_REQUIRED:{captcha_file}"
                except:
                    pass
        
        elif captcha_type == 'math':
            # Simple math CAPTCHA
            question = captcha_data.get('question', '')
            try:
                # Very simple math evaluation (BE CAREFUL WITH eval!)
                if 'What is' in question or 'Calculate' in question:
                    # Extract math expression
                    import re
                    numbers = re.findall(r'\d+', question)
                    if numbers and len(numbers) >= 2:
                        if '+' in question:
                            return str(int(numbers[0]) + int(numbers[1]))
                        elif '-' in question:
                            return str(int(numbers[0]) - int(numbers[1]))
                        elif '×' in question or '*' in question:
                            return str(int(numbers[0]) * int(numbers[1]))
            
            except:
                pass
        
        return "CAPTCHA_SOLUTION_NOT_AVAILABLE"
    
    def launch_tool(self, tool_name):
        """Launch a desktop tool"""
        try:
            if tool_name == 'api_tester':
                import subprocess
                subprocess.Popen(['python', os.path.join(os.path.dirname(__file__), 'api_tester.py')])
                self.active_tools['api_tester'] = True
                return True
            
            elif tool_name == 'sms_panel':
                import subprocess
                subprocess.Popen(['python', os.path.join(os.path.dirname(__file__), 'sms_panel.py')])
                self.active_tools['sms_panel'] = True
                return True
            
            elif tool_name == 'dev_tools':
                # DevTools is browser-based
                return True
            
            else:
                print(f"❌ Unknown tool: {tool_name}")
                return False
        
        except Exception as e:
            print(f"❌ Launch tool error: {e}")
            return False
    
    def get_data_for_browser(self):
        """Get data to send to browser"""
        return {
            'sessions': self.sessions,
            'active_tools': self.active_tools,
            'captcha_services': ['manual', '2captcha', 'anticaptcha'],  # Placeholder
            'timestamp': datetime.now().isoformat()
        }
    
    def export_tool_data(self, tool, format='json'):
        """Export tool data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if tool == 'api_tester':
                # Export captured requests
                export_file = os.path.join(self.data_dir, f"api_requests_{timestamp}.{format}")
                requests = []
                
                # Collect all request files
                for filename in os.listdir(self.data_dir):
                    if filename.startswith('request_'):
                        with open(os.path.join(self.data_dir, filename), 'r') as f:
                            requests.append(json.load(f))
                
                if format == 'json':
                    with open(export_file, 'w') as f:
                        json.dump(requests, f, indent=2)
                elif format == 'csv':
                    import csv
                    with open(export_file, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['URL', 'Method', 'Status', 'Time', 'Size'])
                        for req in requests:
                            writer.writerow([
                                req.get('url', ''),
                                req.get('method', ''),
                                req.get('statusCode', ''),
                                req.get('timestamp', ''),
                                len(str(req.get('responseBody', '')))
                            ])
                
                return export_file
            
            elif tool == 'sms_panel':
                # Export SMS data
                export_file = os.path.join(self.data_dir, f"sms_data_{timestamp}.{format}")
                
                # Collect SMS data
                sms_data = []
                for filename in os.listdir(self.data_dir):
                    if filename.startswith('sms_') or 'message' in filename.lower():
                        try:
                            with open(os.path.join(self.data_dir, filename), 'r') as f:
                                data = json.load(f)
                                if isinstance(data, list):
                                    sms_data.extend(data)
                        except:
                            pass
                
                if format == 'json':
                    with open(export_file, 'w') as f:
                        json.dump(sms_data, f, indent=2)
                elif format == 'csv':
                    import csv
                    with open(export_file, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['From', 'To', 'Message', 'Time', 'Status'])
                        for msg in sms_data:
                            writer.writerow([
                                msg.get('from', ''),
                                msg.get('to', ''),
                                msg.get('body', ''),
                                msg.get('timestamp', ''),
                                msg.get('status', '')
                            ])
                
                return export_file
        
        except Exception as e:
            print(f"❌ Export error: {e}")
            return None
    
    def run(self):
        """Main run loop"""
        print("\n" + "="*60)
        print("TurboX Socket Bridge - Phase 3")
        print("="*60)
        print("Waiting for connections...")
        print(f"Browser Extension should connect to: http://localhost:{self.port}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                time.sleep(1)
                
                # Show status periodically
                if int(time.time()) % 10 == 0:
                    active_clients = len([c for c in self.clients.values() if c.get('socket')])
                    print(f"📊 Status: {active_clients} clients, {len(self.sessions)} sessions")
        
        except KeyboardInterrupt:
            print("\n🔴 Shutting down Socket Bridge...")
            self.ws_running = False
            
            # Close all client connections
            for client_id, client in list(self.clients.items()):
                try:
                    client['socket'].close()
                except:
                    pass
            
            self.http_server.shutdown()
            print("✅ Socket Bridge stopped")

def main():
    """Entry point"""
    bridge = SocketBridge()
    bridge.run()

if __name__ == "__main__":
    main()
