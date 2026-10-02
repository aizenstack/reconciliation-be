import os

_DEFAULT_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://reconciliation-lemon.vercel.app",
)


def _normalize_origin(origin: str) -> str:
    return origin.strip().rstrip("/")


CORS_ORIGINS: list[str] = [_normalize_origin(o) for o in _DEFAULT_ORIGINS]

_extra = os.environ.get("CORS_ORIGINS", "")
if _extra.strip():
    CORS_ORIGINS.extend(
        _normalize_origin(o) for o in _extra.split(",") if o.strip()
    )

_seen: set[str] = set()
CORS_ORIGINS = [o for o in CORS_ORIGINS if not (o in _seen or _seen.add(o))]

CORS_ORIGIN_REGEX = os.environ.get(
    "CORS_ORIGIN_REGEX",
    r"https://([a-z0-9-]+\.)*vercel\.app",
)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = (".xlsx",)

TEMPLATE_HEADERS = ("No", "SKU", "Nama Product", "Stok")
