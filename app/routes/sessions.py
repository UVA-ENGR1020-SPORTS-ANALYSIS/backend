from fastapi import APIRouter

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

from app.models.schemas import CreateSessionRequest
import uuid
import random

@router.post("")
async def create_session(request: CreateSessionRequest):
    # Initial code generation for fallback
    session_code = random.randint(100000, 999999)
    try:
        from app.supabase_wrapper.client import get_client
        supabase = get_client()

        # Ensure uniqueness of the generated code
        while True:
            existing = supabase.table("sessions").select("session_code").eq("session_code", session_code).execute()
            if not existing.data:
                break
            session_code = random.randint(100000, 999999)

        # insert into db
        insert_data = {
            "session_code": session_code,
            "target_teams": request.team_count or 2,
            "status": "waiting"
        }
        res = supabase.table("sessions").insert(insert_data).execute()
        if not res.data:
            return {"session_code": session_code, "session_id": str(uuid.uuid4())}
        return {
            "session_code": res.data[0]["session_code"],
            "session_id": res.data[0]["session_id"]
        }
    except Exception as e:
        print("Falling back to local generated code due to error:", e)
        return {
            "session_code": session_code,
            "session_id": str(uuid.uuid4())
        }

@router.get("")
async def list_sessions():
    # TODO: Fetch all sessions from DB
    return {
        "sessions": [
            {"id": "session_123", "status": "active"}
        ]
    }

@router.get("/{session_id}")
async def get_session_details(session_id: str):
    from fastapi import HTTPException
    try:
        from app.supabase_wrapper.client import get_client
        supabase = get_client()
        session_res = supabase.table("sessions").select("*").eq("session_id", session_id).execute()
        if not session_res.data:
            session_res = supabase.table("sessions").select("*").eq("session_code", int(session_id)).execute()
            if not session_res.data:
                raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_res.data[0]
        teams_res = supabase.table("teams").select("*, player(*)").eq("current_session", session["session_id"]).execute()
        
        return {
            "session": session,
            "teams": teams_res.data or []
        }
    except Exception as e:
        # Mock fallback for UI dev if Supabase is down
        print("Fallback session fetch:", e)
        return {
            "session": {"session_id": session_id, "session_code": session_id, "target_teams": 4, "status": "waiting"},
            "teams": [
                {"team_id": "t1", "player": [{"name": "Lamin"}, {"name": "Sachin"}]},
                {"team_id": "t2", "player": [{"name": "Micah"}, {"name": "Frank"}, {"name": "Nate"}]}
            ]
        }

@router.delete("/{session_id}")
async def end_session(session_id: str):
    # TODO: Archive or delete session in DB
    return {
        "status": "ended",
        "session_id": session_id
    }
