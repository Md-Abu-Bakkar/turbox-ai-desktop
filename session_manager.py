#!/usr/bin/env python3
# ==============================================================================
# TurboX Desktop OS - Session Manager
# Phase 3: Automated Session & Token Management
# ==============================================================================

import os
import sys
import json
import time
import hashlib
import threading
from datetime import datetime, timedelta
from urllib.parse import urlparse
import sqlite3

class SessionManager:
    """Central manager for all authentication sessions and tokens"""
    
    def __init__(self, db_path=None):
        self.home_dir = os.path.expanduser("~")
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        
        if db_path is None:
            db_path = os.path.join(self.config_dir, 'sessions.db')
        
        self.db_path = db_path
        self._init_database()
        
        # Active sessions cache
        self.active_sessions = {}
        self.session_lock = threading.Lock()
        
        # CAPTCHA solutions cache
        self.captcha_cache = {}
        
        # Auto-refresh thread
        self.refresh_thread = threading.Thread(target=self._auto_refresh_sessions, daemon=True)
        self.refresh_thread.start()
    
    def _init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    username TEXT,
                    email TEXT,
                    cookies TEXT,
                    tokens TEXT,
                    headers TEXT,
                    login_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    metadata TEXT
                )
            ''')
            
            # Requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS captured_requests (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    url TEXT NOT NULL,
                    method TEXT,
                    request_headers TEXT,
                    request_body TEXT,
                    response_headers TEXT,
                    response_body TEXT,
                    status_code INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # CAPTCHA solutions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS captcha_solutions (
                    id TEXT PRIMARY KEY,
                    captcha_type TEXT,
                    question TEXT,
                    image_path TEXT,
                    solution TEXT,
                    solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0
                )
            ''')
            
            conn.commit()
    
    def create_session(self, domain, credentials=None):
        """Create a new session for a domain"""
        session_id = hashlib.sha256(f"{domain}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        session_data = {
            'id': session_id,
            'domain': domain,
            'username': credentials.get('username') if credentials else None,
            'email': credentials.get('email') if credentials else None,
            'cookies': json.dumps({}),
            'tokens': json.dumps({}),
            'headers': json.dumps({}),
            'login_data': json.dumps(credentials) if credentials else '{}',
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat(),
            'is_active': 1,
            'metadata': json.dumps({'auto_created': True})
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions 
                (id, domain, username, email, cookies, tokens, headers, login_data, created_at, last_used, expires_at, is_active, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(session_data.values()))
            conn.commit()
        
        # Add to cache
        self.active_sessions[session_id] = session_data
        
        print(f"🔐 Created new session for {domain}: {session_id}")
        return session_id
    
    def update_session(self, session_id, updates):
        """Update session data"""
        with self.session_lock:
            if session_id not in self.active_sessions:
                # Try to load from database
                session = self.get_session(session_id)
                if not session:
                    return False
            
            # Update cache
            if session_id in self.active_sessions:
                self.active_sessions[session_id].update(updates)
                self.active_sessions[session_id]['last_used'] = datetime.now().isoformat()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['cookies', 'tokens', 'headers', 'login_data', 'metadata']:
                        value = json.dumps(value) if isinstance(value, (dict, list)) else value
                    
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                # Add timestamp update
                set_clauses.append("last_used = ?")
                values.append(datetime.now().isoformat())
                
                values.append(session_id)
                
                query = f"UPDATE sessions SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
            
            return True
    
    def get_session(self, session_id):
        """Get session by ID"""
        # Check cache first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Query database
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            row = cursor.fetchone()
            
            if row:
                session = dict(row)
                # Parse JSON fields
                for field in ['cookies', 'tokens', 'headers', 'login_data', 'metadata']:
                    if session[field]:
                        try:
                            session[field] = json.loads(session[field])
                        except:
                            session[field] = {}
                
                # Add to cache
                self.active_sessions[session_id] = session
                return session
        
        return None
    
    def get_session_for_domain(self, domain, create_if_missing=True):
        """Get active session for a domain"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sessions 
                WHERE domain = ? AND is_active = 1 
                ORDER BY last_used DESC 
                LIMIT 1
            ''', (domain,))
            
            row = cursor.fetchone()
            
            if row:
                session = dict(row)
                # Parse JSON fields
                for field in ['cookies', 'tokens', 'headers', 'login_data', 'metadata']:
                    if session[field]:
                        try:
                            session[field] = json.loads(session[field])
                        except:
                            session[field] = {}
                
                # Update cache
                session_id = session['id']
                self.active_sessions[session_id] = session
                
                # Update last used
                cursor.execute('UPDATE sessions SET last_used = ? WHERE id = ?', 
                             (datetime.now().isoformat(), session_id))
                conn.commit()
                
                return session
        
        # Create new session if none exists
        if create_if_missing:
            return self.create_session(domain)
        
        return None
    
    def add_captured_request(self, session_id, request_data):
        """Store a captured request"""
        request_id = hashlib.sha256(
            f"{request_data.get('url')}_{request_data.get('timestamp', '')}".encode()
        ).hexdigest()[:16]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO captured_requests 
                (id, session_id, url, method, request_headers, request_body, 
                 response_headers, response_body, status_code, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request_id,
                session_id,
                request_data.get('url'),
                request_data.get('method'),
                json.dumps(request_data.get('requestHeaders', {})),
                request_data.get('requestBody', ''),
                json.dumps(request_data.get('responseHeaders', {})),
                request_data.get('responseBody', ''),
                request_data.get('statusCode'),
                request_data.get('timestamp', datetime.now().isoformat())
            ))
            
            conn.commit()
        
        return request_id
    
    def get_requests_for_session(self, session_id, limit=100):
        """Get captured requests for a session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM captured_requests 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            
            requests = []
            for row in rows:
                req = dict(row)
                # Parse JSON fields
                for field in ['request_headers', 'response_headers']:
                    if req[field]:
                        try:
                            req[field] = json.loads(req[field])
                        except:
                            req[field] = {}
                
                requests.append(req)
            
            return requests
    
    def extract_tokens_from_request(self, session_id, request_data):
        """Extract tokens from a captured request/response"""
        session = self.get_session(session_id)
        if not session:
            return
        
        new_tokens = {}
        new_cookies = {}
        
        # Extract from response headers
        response_headers = request_data.get('responseHeaders', {})
        
        # Cookies
        set_cookie = response_headers.get('set-cookie', response_headers.get('Set-Cookie', ''))
        if set_cookie:
            for cookie in str(set_cookie).split(';'):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    key = key.strip()
                    value = value.split(';')[0].strip()  # Remove cookie attributes
                    
                    if any(token in key.lower() for token in ['session', 'token', 'auth', 'jwt']):
                        new_cookies[key] = value
        
        # Extract from response body
        response_body = request_data.get('responseBody', '')
        if response_body:
            try:
                body_json = json.loads(response_body)
                if isinstance(body_json, dict):
                    for key, value in body_json.items():
                        key_lower = key.lower()
                        if any(token in key_lower for token in ['token', 'access', 'refresh', 'auth', 'bearer']):
                            if isinstance(value, str) and len(value) > 10:
                                new_tokens[key] = value
            except:
                pass
        
        # Update session with new tokens
        if new_tokens:
            current_tokens = session.get('tokens', {})
            current_tokens.update(new_tokens)
            self.update_session(session_id, {'tokens': current_tokens})
        
        if new_cookies:
            current_cookies = session.get('cookies', {})
            current_cookies.update(new_cookies)
            self.update_session(session_id, {'cookies': current_cookies})
        
        return len(new_tokens) > 0 or len(new_cookies) > 0
    
    def get_auth_for_url(self, url):
        """Get authentication headers/cookies for a URL"""
        domain = urlparse(url).netloc
        
        session = self.get_session_for_domain(domain, create_if_missing=False)
        if not session:
            return {}
        
        auth_headers = {}
        
        # Add cookies
        cookies = session.get('cookies', {})
        if cookies:
            cookie_header = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            auth_headers['Cookie'] = cookie_header
        
        # Add bearer token if available
        tokens = session.get('tokens', {})
        for token_name, token_value in tokens.items():
            if 'bearer' in token_name.lower() or 'access' in token_name.lower():
                auth_headers['Authorization'] = f'Bearer {token_value}'
                break
        
        # Add custom headers from session
        headers = session.get('headers', {})
        auth_headers.update(headers)
        
        return auth_headers
    
    def solve_captcha(self, captcha_data, auto_solve=True):
        """Solve CAPTCHA using cache or external service"""
        captcha_type = captcha_data.get('type', 'unknown')
        question = captcha_data.get('question', '')
        image_data = captcha_data.get('image', '')
        
        # Generate cache key
        if question:
            cache_key = hashlib.md5(question.encode()).hexdigest()
        elif image_data:
            cache_key = hashlib.md5(image_data.encode()).hexdigest()[:32]
        else:
            cache_key = None
        
        # Check cache
        if cache_key and cache_key in self.captcha_cache:
            cached = self.captcha_cache[cache_key]
            if time.time() - cached['timestamp'] < 300:  # 5 minutes cache
                print(f"✅ Using cached CAPTCHA solution")
                return cached['solution']
        
        # Try to solve
        solution = None
        
        if captcha_type == 'math' and question:
            # Simple math CAPTCHA
            try:
                import re
                # Extract numbers and operation
                numbers = re.findall(r'\d+', question)
                if len(numbers) >= 2:
                    if 'plus' in question.lower() or '+' in question:
                        solution = str(int(numbers[0]) + int(numbers[1]))
                    elif 'minus' in question.lower() or '-' in question:
                        solution = str(int(numbers[0]) - int(numbers[1]))
                    elif 'times' in question.lower() or '×' in question or '*' in question:
                        solution = str(int(numbers[0]) * int(numbers[1]))
                    elif 'divide' in question.lower() or '÷' in question or '/' in question:
                        if int(numbers[1]) != 0:
                            solution = str(int(numbers[0]) // int(numbers[1]))
            except:
                pass
        
        elif captcha_type == 'image' and image_data and auto_solve:
            # Save image for external solving
            import base64
            try:
                image_bytes = base64.b64decode(image_data)
                captcha_dir = os.path.join(self.config_dir, 'captchas')
                os.makedirs(captcha_dir, exist_ok=True)
                
                filename = f"captcha_{int(time.time())}.png"
                filepath = os.path.join(captcha_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                print(f"📸 CAPTCHA image saved: {filepath}")
                
                # Try external service (placeholder for Phase 3)
                solution = self._call_captcha_service(filepath)
                
                if not solution:
                    solution = f"MANUAL:{filepath}"
            
            except Exception as e:
                print(f"❌ CAPTCHA image processing error: {e}")
        
        # Cache solution
        if solution and cache_key:
            self.captcha_cache[cache_key] = {
                'solution': solution,
                'timestamp': time.time()
            }
            
            # Also save to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                captcha_id = hashlib.md5(str(captcha_data).encode()).hexdigest()[:16]
                
                cursor.execute('''
                    INSERT OR REPLACE INTO captcha_solutions 
                    (id, captcha_type, question, image_path, solution, solved_at, used_count)
                    VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT used_count FROM captcha_solutions WHERE id = ?), 0) + 1)
                ''', (
                    captcha_id,
                    captcha_type,
                    question,
                    filepath if 'filepath' in locals() else None,
                    solution,
                    datetime.now().isoformat(),
                    captcha_id
                ))
                
                conn.commit()
        
        return solution
    
    def _call_captcha_service(self, image_path):
        """Call external CAPTCHA solving service (placeholder)"""
        # This would integrate with 2Captcha, Anti-Captcha, etc.
        # For Phase 3, return None to trigger manual solving
        
        print(f"⚠️  External CAPTCHA service not configured in Phase 3")
        print(f"   Image saved for manual solving: {image_path}")
        
        return None
    
    def auto_login(self, domain, login_url, credentials):
        """Attempt automatic login using captured login patterns"""
        session = self.get_session_for_domain(domain)
        if not session:
            session_id = self.create_session(domain, credentials)
            session = self.get_session(session_id)
        
        # Check if we have login pattern for this domain
        login_patterns = self._get_login_patterns(domain)
        
        if login_patterns:
            # Use captured login pattern
            print(f"🔐 Attempting auto-login to {domain}")
            return self._execute_auto_login(domain, login_patterns[0], credentials)
        else:
            print(f"⚠️  No login pattern found for {domain}")
            return False
    
    def _get_login_patterns(self, domain):
        """Get saved login patterns for a domain"""
        patterns = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM captured_requests 
                WHERE url LIKE ? AND request_body LIKE ? 
                ORDER BY timestamp DESC 
                LIMIT 5
            ''', (f'%{domain}%', '%password%'))
            
            rows = cursor.fetchall()
            
            for row in rows:
                patterns.append(dict(row))
        
        return patterns
    
    def _execute_auto_login(self, domain, login_pattern, credentials):
        """Execute automatic login using pattern"""
        # This would use requests/selenium to auto-login
        # Placeholder for Phase 3
        print(f"⚠️  Auto-login execution not implemented in Phase 3")
        return False
    
    def _auto_refresh_sessions(self):
        """Background thread to refresh expiring sessions"""
        while True:
            time.sleep(60)  # Check every minute
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Find sessions expiring soon
                    cursor.execute('''
                        SELECT id FROM sessions 
                        WHERE expires_at < ? AND is_active = 1
                    ''', ((datetime.now() + timedelta(hours=1)).isoformat(),))
                    
                    expiring = cursor.fetchall()
                    
                    for (session_id,) in expiring:
                        print(f"🔄 Session {session_id} expiring soon")
                        # Attempt refresh (placeholder)
                        # self._refresh_session(session_id)
            
            except Exception as e:
                print(f"⚠️  Session refresh error: {e}")
    
    def export_sessions(self, output_format='json'):
        """Export all sessions and data"""
        export_data = {
            'sessions': [],
            'requests': [],
            'captchas': [],
            'exported_at': datetime.now().isoformat()
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Export sessions
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions')
            for row in cursor.fetchall():
                session = dict(row)
                # Parse JSON fields
                for field in ['cookies', 'tokens', 'headers', 'login_data', 'metadata']:
                    if session[field]:
                        try:
                            session[field] = json.loads(session[field])
                        except:
                            session[field] = {}
                
                export_data['sessions'].append(session)
            
            # Export recent requests
            cursor.execute('SELECT * FROM captured_requests ORDER BY timestamp DESC LIMIT 1000')
            for row in cursor.fetchall():
                export_data['requests'].append(dict(row))
            
            # Export CAPTCHA solutions
            cursor.execute('SELECT * FROM captcha_solutions')
            for row in cursor.fetchall():
                export_data['captchas'].append(dict(row))
        
        # Save to file
        export_dir = os.path.join(self.config_dir, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        filename = f"sessions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
        filepath = os.path.join(export_dir, filename)
        
        if output_format == 'json':
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
        elif output_format == 'csv':
            # Simplified CSV export
            import csv
            
            # Write sessions
            with open(filepath.replace('.csv', '_sessions.csv'), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Domain', 'Username', 'Created', 'Last Used'])
                for session in export_data['sessions']:
                    writer.writerow([
                        session.get('id'),
                        session.get('domain'),
                        session.get('username'),
                        session.get('created_at'),
                        session.get('last_used')
                    ])
            
            # Write requests
            with open(filepath.replace('.csv', '_requests.csv'), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Method', 'Status', 'Time'])
                for req in export_data['requests']:
                    writer.writerow([
                        req.get('url'),
                        req.get('method'),
                        req.get('status_code'),
                        req.get('timestamp')
                    ])
        
        print(f"✅ Sessions exported to: {filepath}")
        return filepath

def main():
    """Command-line interface"""
    manager = SessionManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            sessions = manager.get_all_sessions()
            print(f"📋 Active Sessions ({len(sessions)}):")
            for session in sessions:
                print(f"  {session['id']}: {session['domain']} ({session['username']})")
        
        elif command == 'export':
            format = sys.argv[2] if len(sys.argv) > 2 else 'json'
            filepath = manager.export_sessions(format)
            print(f"✅ Exported to: {filepath}")
        
        elif command == 'cleanup':
            # Clean expired sessions
            print("🧹 Cleanup feature coming in Phase 3")
        
        else:
            print("Commands: list, export [json|csv], cleanup")
    else:
        print("TurboX Session Manager")
        print("Usage: python session_manager.py [command]")
        print("\nManages authentication sessions, tokens, and CAPTCHA solutions")

if __name__ == "__main__":
    main()
