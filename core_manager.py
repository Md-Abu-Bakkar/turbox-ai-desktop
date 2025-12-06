#!/data/data/com.termux/files/usr/bin/python3
# ==============================================================================
# TurboX Desktop OS - Core System Manager
# Phase 1: Foundation Service
# ==============================================================================

import os
import sys
import json
import time
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime

class TurboXCoreManager:
    """Central manager for TurboX Desktop OS services"""
    
    def __init__(self):
        self.home_dir = str(Path.home())
        self.config_dir = os.path.join(self.home_dir, '.turboX')
        self.config_file = os.path.join(self.config_dir, 'config', 'system.json')
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Load or create config
        self.config = self._load_config()
        
        # Service tracking
        self.services = {}
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        dirs = [
            self.config_dir,
            os.path.join(self.config_dir, 'config'),
            os.path.join(self.config_dir, 'scripts'),
            os.path.join(self.config_dir, 'tools'),
            os.path.join(self.config_dir, 'logs'),
            os.path.join(self.home_dir, 'Desktop'),
            os.path.join(self.home_dir, 'Documents'),
            os.path.join(self.home_dir, 'Downloads'),
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def _load_config(self):
        """Load or create system configuration"""
        default_config = {
            "system": {
                "version": "1.0.0",
                "phase": 1,
                "last_start": datetime.now().isoformat()
            },
            "desktop": {
                "theme": "windows-dark",
                "taskbar_visible": True,
                "start_menu_enabled": True,
                "window_effects": True
            },
            "tools": {
                "api_tester": {"enabled": False, "auto_start": False},
                "sms_panel": {"enabled": False, "auto_start": False},
                "dev_tools": {"enabled": False, "auto_start": False}
            },
            "storage": {
                "phone_storage_mounted": False,
                "sync_enabled": True,
                "download_path": os.path.join(self.home_dir, 'Downloads')
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                return default_config
        except Exception as e:
            print(f"⚠️  Config load error: {e}, using defaults")
            return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        self.config['system']['last_save'] = datetime.now().isoformat()
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("✅ Configuration saved")
        except Exception as e:
            print(f"❌ Config save error: {e}")
    
    def start_service(self, service_name, command):
        """Start a system service"""
        if service_name in self.services:
            print(f"⚠️  Service '{service_name}' already running")
            return False
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.services[service_name] = {
                'process': process,
                'command': command,
                'started': datetime.now().isoformat()
            }
            
            # Start monitor thread
            monitor_thread = threading.Thread(
                target=self._monitor_service,
                args=(service_name, process),
                daemon=True
            )
            monitor_thread.start()
            
            print(f"✅ Started service: {service_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start service '{service_name}': {e}")
            return False
    
    def _monitor_service(self, service_name, process):
        """Monitor a service process"""
        stdout, stderr = process.communicate()
        
        if process.returncode != 0 and self.running:
            print(f"⚠️  Service '{service_name}' exited with code {process.returncode}")
            if stderr:
                print(f"   Error: {stderr[:200]}")
        
        # Clean up
        if service_name in self.services:
            del self.services[service_name]
    
    def stop_service(self, service_name):
        """Stop a running service"""
        if service_name not in self.services:
            print(f"⚠️  Service '{service_name}' not found")
            return False
        
        service = self.services[service_name]
        try:
            service['process'].terminate()
            # Wait a bit then kill if needed
            time.sleep(1)
            if service['process'].poll() is None:
                service['process'].kill()
            
            del self.services[service_name]
            print(f"✅ Stopped service: {service_name}")
            return True
        except Exception as e:
            print(f"❌ Error stopping service '{service_name}': {e}")
            return False
    
    def check_system_health(self):
        """Check system health and report status"""
        health = {
            "x11_running": False,
            "window_manager": False,
            "taskbar": False,
            "storage_mounted": False,
            "errors": []
        }
        
        # Check X11 server
        try:
            result = subprocess.run(
                ["pgrep", "-x", "termux-x11"],
                capture_output=True,
                text=True
            )
            health["x11_running"] = result.returncode == 0
        except Exception as e:
            health["errors"].append(f"X11 check failed: {e}")
        
        # Check window manager
        try:
            result = subprocess.run(
                ["pgrep", "-x", "openbox"],
                capture_output=True,
                text=True
            )
            health["window_manager"] = result.returncode == 0
        except Exception as e:
            health["errors"].append(f"WM check failed: {e}")
        
        # Check storage mount
        storage_path = "/storage/emulated/0"
        health["storage_mounted"] = os.path.exists(storage_path)
        
        return health
    
    def mount_phone_storage(self):
        """Mount phone storage to desktop"""
        storage_path = "/storage/emulated/0"
        mount_point = os.path.join(self.home_dir, "PhoneStorage")
        
        if not os.path.exists(storage_path):
            print("❌ Phone storage not accessible")
            return False
        
        try:
            os.makedirs(mount_point, exist_ok=True)
            # Create symlink for easy access
            link_path = os.path.join(self.home_dir, "Desktop", "Phone")
            if os.path.exists(link_path):
                os.remove(link_path)
            os.symlink(mount_point, link_path)
            
            self.config['storage']['phone_storage_mounted'] = True
            self.save_config()
            
            print(f"✅ Phone storage mounted at: {link_path}")
            return True
        except Exception as e:
            print(f"❌ Storage mount failed: {e}")
            return False
    
    def log_system_event(self, event_type, message):
        """Log system events"""
        log_file = os.path.join(self.config_dir, 'logs', 'system.log')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"[{timestamp}] [{event_type}] {message}\n"
        
        try:
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except Exception:
            pass  # Don't crash if logging fails
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown of all services"""
        print("\n🔴 Shutting down TurboX Core Manager...")
        self.running = False
        
        # Stop all services
        for service_name in list(self.services.keys()):
            self.stop_service(service_name)
        
        self.save_config()
        print("✅ TurboX shutdown complete")
        sys.exit(0)
    
    def run(self):
        """Main run loop"""
        print("""
╔══════════════════════════════════════════╗
║     TurboX Core Manager (Phase 1)       ║
║     System Status: ACTIVE               ║
╚══════════════════════════════════════════╝
        """)
        
        # Log startup
        self.log_system_event("STARTUP", "Core Manager started")
        
        # Attempt to mount phone storage
        if not self.config['storage']['phone_storage_mounted']:
            print("🔧 Attempting to mount phone storage...")
            self.mount_phone_storage()
        
        # Main monitoring loop
        last_health_check = 0
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic health check every 30 seconds
                if current_time - last_health_check > 30:
                    health = self.check_system_health()
                    
                    if not health["x11_running"]:
                        print("⚠️  X11 server not detected")
                    
                    last_health_check = current_time
                
                time.sleep(5)  # Main loop sleep
                
            except KeyboardInterrupt:
                self.shutdown()
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(10)

def main():
    """Entry point"""
    manager = TurboXCoreManager()
    
    # Start essential services
    print("🚀 Starting essential services...")
    
    # Start desktop notification service (placeholder for Phase 2)
    manager.start_service(
        "notify_daemon",
        "python -c 'import time; time.sleep(86400)'"
    )
    
    # Run main loop
    manager.run()

if __name__ == "__main__":
    main()
