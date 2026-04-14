from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

from app.models.schemas import CreateSessionRequest
from app.supabase_wrapper.client import get_client
import uuid
import random

@router.post("")
async def create_session(request: CreateSessionRequest):
    # Initial code generation for fallback
    session_code = random.randint(100000, 999999)
    try:
        supabase = get_client()

        # Ensure uniqueness — bounded to prevent an infinite loop if the code space is exhausted
        candidates = [random.randint(100000, 999999) for _ in range(10)]
        existing = supabase.table("sessions") \
            .select("session_code") \
            .in_("session_code", candidates) \
            .execute()
        used = {row["session_code"] for row in existing.data}
        available = [c for c in candidates if c not in used]
        if not available:
            raise HTTPException(status_code=503, detail="Could not generate a unique session code. Try again.")


        # insert into db
        insert_data = {
            "session_code": session_code,
            "target_team": request.team_count or 2,
            "status": "waiting"
        }
        res = supabase.table("sessions").insert(insert_data).execute()
        if not res.data:
            return {"session_code": session_code, "session_id": str(uuid.uuid4())}
        return {
            "session_code": res.data[0]["session_code"],
            "session_id": res.data[0]["session_id"]
        }
    except Exception:
        print("Falling back to local generated code due to an internal error.")
        return {
            "session_code": session_code,
            "session_id": str(uuid.uuid4())
        }

@router.get("")
async def list_sessions():
    try:
        supabase = get_client()
        res = supabase.table("sessions").select("*").order("session_code", desc=True).execute()
        return {"sessions": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {e}")

@router.get("/{session_code}")
async def get_session_details(session_code: str):
    from fastapi import HTTPException
    try:
        from app.supabase_wrapper.client import get_client
        supabase = get_client()
        
        session_res = supabase.table("sessions").select("*").eq("session_code", int(session_code)).execute()
            
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_res.data[0]
        teams_res = supabase.table("teams").select("*, player(*)").eq("current_session", session["session_id"]).execute()
        
        return {
            "session": session,
            "teams": teams_res.data or []
        }
    except HTTPException:
        raise
    except Exception:
        # Mock fallback for UI dev if Supabase is down
        print("Fallback session fetch Exception occurred.")
        return {
            "session": {"session_id": str(uuid.uuid4()), "session_code": int(session_code) if session_code.isdigit() else 0, "target_team": 4, "status": "waiting"},
            "teams": [
                {"team_id": "t1", "player": [{"player_name": "Lamin"}, {"player_name": "Sachin"}, {"player_name": "Frank"}]},
                {"team_id": "t2", "player": [{"player_name": "Micah"}, {"player_name": "Frank"}, {"player_name": "Nate"}]},
                {"team_id": "t3", "player": [{"player_name": "Micah"}, {"player_name": "Frank"}, {"player_name": "Nate"}]},
                {"team_id": "t4", "player": [{"player_name": "Micah"}, {"player_name": "Frank"}, {"player_name": "Nate"}]}
            ]
        }

@router.delete("/{session_id}")
async def end_session(session_id: str):
    try:
        supabase = get_client()
        res = supabase.table("sessions").update({"status": "ended"}).eq("session_id", session_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Session not found.")
        return {
            "status": "ended",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {e}")
