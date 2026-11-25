from pathlib import Path
import uuid
from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import BadRequestError

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class StorageService:
    def save_product_image(self, file: UploadFile) -> str:
        filename = file.filename or ""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise BadRequestError("Unsupported image format. Allowed: jpg, jpeg, png, webp.")
        if file.content_type and file.content_type.lower() not in ALLOWED_IMAGE_MIME_TYPES:
            raise BadRequestError("Invalid image content type.")

        content = file.file.read(MAX_IMAGE_SIZE_BYTES + 1)
        if len(content) == 0:
            raise BadRequestError("Uploaded image file is empty.")
        if len(content) > MAX_IMAGE_SIZE_BYTES:
            raise BadRequestError("Image exceeds 5 MB limit.")

        settings = get_settings()
        upload_dir = Path(settings.local_upload_dir) / "products"
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{uuid.uuid4().hex}{ext}"
        dest = upload_dir / safe_name
        dest.write_bytes(content)
        return f"/uploads/products/{safe_name}"

