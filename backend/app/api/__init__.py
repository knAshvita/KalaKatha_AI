from app.api.artwork import router as artwork_router
from app.api.ask import router as ask_router
from app.api.narrate import router as narrate_router
from app.api.health import router as health_router

__all__ = ["artwork_router", "ask_router", "narrate_router", "health_router"]
