import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Optional, Tuple

# ----------------------------
# Global constants
# ----------------------------
BASE_UPLOAD_DIR = Path("app/uploads")
PROFILE_DIR = BASE_UPLOAD_DIR / "profile_photos"
MEDIA_ROOT = BASE_UPLOAD_DIR
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_DOC_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ----------------------------
# File validation helpers
# ----------------------------
def is_valid_extension(filename: str, allowed_exts: set) -> bool:
    if not filename:
        return False
    return Path(filename).suffix.lower() in allowed_exts


def is_file_clean(file_obj: UploadFile) -> bool:
    """Dummy virus scan — replace with actual antivirus integration (e.g. ClamAV)."""
    return True


# ----------------------------
# Profile photo upload
# ----------------------------
def save_profile_photo(file: UploadFile, user_id: int) -> str:
    """Validate and save a user's profile photo."""
    if not is_valid_extension(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG and PNG allowed.")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size too large. Maximum 5MB allowed.")

    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"user_{user_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = PROFILE_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    return str(file_path)


def delete_profile_photo(file_path: str) -> bool:
    """Safely delete a user's profile photo if it exists."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False


def get_profile_photo_url(file_path: Optional[str]) -> Optional[str]:
    """Convert stored file path to public static URL."""
    if not file_path:
        return None
    relative_path = file_path.replace("app/", "")
    return f"/static/{relative_path}"


# ----------------------------
# General-purpose file validation (for donations, PAN docs, etc.)
# ----------------------------
def validate_and_save_file(
    file_obj: Optional[UploadFile],
    subdir: str,
    field_label: str,
    user_type: str = "common"
) -> Tuple[str, Optional[str]]:
    """
    Validate and save uploaded PDF or image file.
    Returns (relative_path, error_message)
    """
    if not file_obj:
        return "", f"{field_label} is required. (Validation failed)"

    ext = Path(file_obj.filename).suffix.lower()
    if ext not in ALLOWED_DOC_EXTENSIONS:
        return "", f"{field_label} must be a PDF or image file."

    # Determine file size
    file_obj.file.seek(0, 2)
    file_size = file_obj.file.tell()
    file_obj.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return "", f"{field_label} must be under 5MB."

    if not is_file_clean(file_obj):
        return "", f"{field_label} failed virus scan."

    # Prepare upload directory
    upload_dir = MEDIA_ROOT / f"{user_type}_docs" / subdir
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj.file, buffer)
    except Exception as e:
        return "", f"Failed to save {field_label}: {str(e)}"

    relative_path = str(file_path.relative_to(MEDIA_ROOT))
    return relative_path, None
