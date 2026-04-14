import os
import secrets

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes.connect import router as connect_router
from app.routes.game import router as game_router
from app.routes.players import router as players_router
from app.routes.sessions import router as sessions_router
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(
    title="Sports Analysis App API",
    description="API for analyzing sports data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-bc7.pages.dev", # production frontend
        "https://tabletopbb.app", # new production root domain
        "https://www.tabletopbb.app", # www alias
        "http://localhost:5173" # Vite local server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Sports Analysis App API is running..."}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/warmup")
async def warmup(x_warmup_key: str | None = Header(default=None)):
    expected_key = os.getenv("WARMUP_KEY")
    if expected_key and not secrets.compare_digest(expected_key, x_warmup_key or ""):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "warmed"}

app.include_router(connect_router)
app.include_router(game_router)
app.include_router(players_router)
app.include_router(sessions_router)

if __name__ == "__main__":
    import uvicorn
    from app.config import PORT

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT)
