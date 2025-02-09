from fastapi import FastAPI

from app.routes.user_routes import router as user_router
from app.routes.game_routes import router as game_router

app = FastAPI()

app.include_router(user_router, prefix="/api/v1")
app.include_router(game_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to ..."}