from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.router import router as v1_router
from app.infrastructure.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application")
    init_db()
    yield
    print("Shutting down application")


app = FastAPI(
    title="PR Reviewer Assignment Service",
    lifespan=lifespan
)

app.include_router(v1_router)
