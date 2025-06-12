"""
Popup module for RAT client
Shows Windows message boxes using ctypes WinAPI
"""

import ctypes
from ctypes import wintypes
import sys

# Windows MessageBox constants
MB_OK = 0x00000000
MB_OKCANCEL = 0x00000001
MB_ABORTRETRYIGNORE = 0x00000002
MB_YESNOCANCEL = 0x00000003
MB_YESNO = 0x00000004
MB_RETRYCANCEL = 0x00000005

MB_ICONERROR = 0x00000010
MB_ICONQUESTION = 0x00000020
MB_ICONWARNING = 0x00000030
MB_ICONINFORMATION = 0x00000040

def show_popup(title: str = "Message", message: str = "Hello from RAT!", 
               style: int = MB_OK | MB_ICONINFORMATION) -> int:
    """
    Show a Windows message box popup
    
    Args:
        title: Window title
        message: Message text
        style: MessageBox style (buttons and icon)
    
    Returns:
        Button pressed (1=OK, 2=Cancel, etc.) or 0 if error
    """
    try:
        # Only works on Windows
        if sys.platform != "win32":
            print("Popup only supported on Windows")
            return 0
            
        # Get MessageBoxW function
        user32 = ctypes.windll.user32
        
        # Show message box
        result = user32.MessageBoxW(
            0,  # hWnd (parent window handle, 0 = desktop)
            message,  # lpText
            title,  # lpCaption
            style  # uType
        )
        
        return result
        
    except Exception as e:
        print(f"Popup error: {e}")
        return 0

def show_info_popup(title: str, message: str) -> int:
    """Show information popup with OK button"""
    return show_popup(title, message, MB_OK | MB_ICONINFORMATION)

def show_warning_popup(title: str, message: str) -> int:
    """Show warning popup with OK button"""
    return show_popup(title, message, MB_OK | MB_ICONWARNING)

def show_error_popup(title: str, message: str) -> int:
    """Show error popup with OK button"""
    return show_popup(title, message, MB_OK | MB_ICONERROR)

def show_question_popup(title: str, message: str) -> int:
    """Show question popup with Yes/No buttons"""
    return show_popup(title, message, MB_YESNO | MB_ICONQUESTION) 