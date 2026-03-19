from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.connect import router as connect_router

app = FastAPI(
    title="Sports Analysis App API",
    description="API for analyzing sports data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-bc7.pages.dev/", # production frontend
        "http://localhost:5173/" # Vite local server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Sports Analysis App API is running..."}

app.include_router(connect_router)

if __name__ == "__main__":
    import uvicorn
    from app.config import PORT

    uvicorn.run("app.main:app", host="[IP_ADDRESS]", port=PORT, reload=True)
