"""
Communication Protocol for RAT Demo
Defines JSON message formats and protocol handling
"""

import json
import base64
from typing import Dict, Any, Optional

class Protocol:
    """Handles message serialization/deserialization for RAT communication"""
    
    @staticmethod
    def create_command(cmd: str, **kwargs) -> str:
        """Create a command message to send to client"""
        message = {
            "cmd": cmd,
            **kwargs
        }
        return json.dumps(message) + "\n"
    
    @staticmethod
    def create_response(response_type: str, payload: Any = None, status: str = "ok") -> str:
        """Create a response message from client to server"""
        message = {
            "type": response_type,
            "status": status
        }
        if payload is not None:
            message["payload"] = payload
        return json.dumps(message) + "\n"
    
    @staticmethod
    def parse_message(data: str) -> Optional[Dict[str, Any]]:
        """Parse incoming JSON message"""
        try:
            data = data.strip()
            if not data:
                return None
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def encode_image(image_path: str) -> str:
        """Encode image file to base64 string"""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    @staticmethod
    def decode_image(base64_data: str, output_path: str) -> None:
        """Decode base64 string to image file"""
        image_data = base64.b64decode(base64_data)
        with open(output_path, "wb") as img_file:
            img_file.write(image_data)

# Command constants
class Commands:
    PING = "ping"
    SCREENSHOT = "screenshot"
    POPUP = "popup"
    QUIT = "quit"

# Response types
class ResponseTypes:
    PONG = "pong"
    SCREENSHOT = "screenshot"
    POPUP = "popup"
    ERROR = "error" 