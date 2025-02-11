from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler # type: ignore
from contextlib import asynccontextmanager
from app.utils.utils import get_game_popularity_index

from app.routes.user_routes import router as user_router
from app.routes.game_routes import router as game_router
from app.routes.game_session_routes import router as game_session_router
from app.routes.leaderboard_routes import router as leaderboard_router

app = FastAPI()

app.include_router(user_router, prefix="/api/v1")
app.include_router(game_router, prefix="/api/v1")
app.include_router(game_session_router, prefix="/api/v1")
app.include_router(leaderboard_router, prefix="/api/v1")

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown of scheduler to fetch latest popularity index from server."""
    scheduler.add_job(get_game_popularity_index, "interval", minutes=5)
    scheduler.start()
    print("Scheduler started ✅")
    yield
    scheduler.shutdown()
    print("Scheduler shut down 🛑")

app.router.lifespan_context = lifespan

@app.get("/")
async def root():
    return {"message": "Welcome to ..."}