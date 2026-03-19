from fastapi import APIRouter

router = APIRouter()

@router.get("/api/connect/{session_code}")
async def connect(session_code: str):
    return {"message": f"attempted join {session_code}"}
