from app.routes.auth import router as auth_router
from app.routes.health import router as health_router
from app.routes.stakers import router as stakers_router
from app.routes.validators import router as validators_router

__all__ = ["auth_router", "health_router", "stakers_router", "validators_router"]
