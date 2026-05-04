from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import init_db
from app.routes import (
    auth_router,
    epochs_router,
    health_router,
    policies_router,
    rewards_router,
    stakers_router,
    stakes_router,
    validators_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(validators_router)
app.include_router(stakers_router)
app.include_router(policies_router)
app.include_router(stakes_router)
app.include_router(epochs_router)
app.include_router(rewards_router)
