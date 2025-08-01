import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
import shutil

# Directory to store profile photos
UPLOAD_DIR = Path("app/uploads/profile_photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_valid_image(file: UploadFile) -> bool:
    if not file.filename:
        return False
    
    file_ext = Path(file.filename).suffix.lower()
    return file_ext in ALLOWED_EXTENSIONS

def save_profile_photo(file: UploadFile, user_id: int) -> str:
    if not is_valid_image(file):
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, GIF, WEBP allowed.")
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size too large. Maximum 5MB allowed.")
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"user_{user_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    return str(file_path)

def delete_profile_photo(file_path: str) -> bool:
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False

def get_profile_photo_url(file_path: str) -> str:
    """Convert file path to accessible URL"""
    if not file_path:
        return None
    
    relative_path = file_path.replace("app/", "")
    return f"/static/{relative_path}"
