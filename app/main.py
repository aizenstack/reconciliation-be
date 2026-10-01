from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.reconciliation import router as reconciliation_router
from app.core.config import CORS_ORIGINS


def create_app() -> FastAPI:
    app = FastAPI(title="Data Reconciliation API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(reconciliation_router)
    return app


app = create_app()
