import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.services.logging_setup import JsonFormatter
from app.routes import agents as agents_routes
from app.routes import orchestrator as orchestrator_routes
from app.routes import public as public_routes


def configure_logging():
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    if settings.log_json:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        root = logging.getLogger()
        root.handlers = []
        root.setLevel(level)
        root.addHandler(handler)
    else:
        logging.basicConfig(
            level=level,
            stream=sys.stdout,
            format='%(asctime)s %(levelname)s %(name)s %(message)s',
        )


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(agents_routes.router,
                       prefix="/api/agents", tags=["agents"])
    app.include_router(orchestrator_routes.router,
                       prefix="/api/orchestrator", tags=["orchestrator"])
    app.include_router(public_routes.router, tags=["public"])
    return app


app = create_app()
