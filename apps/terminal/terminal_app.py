import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading

class TerminalApp:
    def __init__(self):
        self.window = None
        self.process = None
        
    def launch(self):
        """Launch terminal window"""
        self.window = tk.Toplevel()
        self.window.title("TurboX Terminal")
        self.window.geometry("800x500")
        
        # Terminal output
        self.output_text = scrolledtext.ScrolledText(
            self.window,
            wrap=tk.WORD,
            bg='black',
            fg='white',
            font=('Courier New', 11)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input frame
        input_frame = ttk.Frame(self.window)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.input_entry = ttk.Entry(input_frame, font=('Courier New', 11))
        self.input_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.input_entry.bind('<Return>', self._execute_command)
        
        ttk.Button(input_frame, text="Run", command=self._execute_command).pack(side=tk.RIGHT, padx=5)
        
        # Welcome message
        self._print_output("🚀 TurboX Terminal - Ready\nType 'help' for commands\n")
        
    def _execute_command(self, event=None):
        """Execute terminal command"""
        command = self.input_entry.get().strip()
        if not command:
            return
            
        self.input_entry.delete(0, tk.END)
        self._print_output(f"$ {command}\n")
        
        # Run command in thread
        threading.Thread(target=self._run_command, args=(command,), daemon=True).start()
    
    def _run_command(self, command):
        """Run command and capture output"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            output = result.stdout if result.stdout else result.stderr
            self._print_output(output + "\n")
            
        except subprocess.TimeoutExpired:
            self._print_output("Command timed out\n")
        except Exception as e:
            self._print_output(f"Error: {str(e)}\n")
    
    def _print_output(self, text):
        """Print text to terminal output"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.update()
    
    def close(self):
        """Close terminal"""
        if self.window:
            self.window.destroy()
