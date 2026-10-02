import os

CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173", "https://reconciliation-be.vercel.app", "https://reconciliation-lemon.vercel.app/"]

_extra = os.environ.get("CORS_ORIGINS", "")
if _extra.strip():
    CORS_ORIGINS.extend(o.strip() for o in _extra.split(",") if o.strip())

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = (".xlsx",)

TEMPLATE_HEADERS = ("No", "SKU", "Nama Product", "Stok")
