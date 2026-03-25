# API and Schema Changes Update

**Date:** March 24, 2026
**Focus:** Database Schema Finalization & Session Join Validation

## 1. Database Schema Updates (`app/models/schema.md`)
The initial schema design has been upgraded to properly support a standard relational database (like Supabase).

* **Added `Team Info` representation**: Explicitly separated "Teams" from "Players" to manage win/loss records and rosters properly.
* **Added Critical Missing Fields**: 
    * `Player Info`: Added an auto-generated `Player Index` to act as a simple numerical identifier (non-customizable).
    * `The Live Game`: Added `status` ("waiting", "in_progress", "completed") and timestamps to track if the session is joinable.
    * `Shot History`: Added `Timestamp` / `Game Clock` and `Shot ID` (Primary Key). Without timestamps, chronological play-by-play analytics would be impossible.
* **Defined Primary & Foreign Keys**: Structured the relationships (e.g., `shot_log` references a specific `game_session_id`).

## 2. API Endpoint Change: `POST /api/connect`
**CRITICAL CHANGE FOR FRONTEND IMPLEMENTATION:** 
The endpoint for a player joining a session no longer uses URL query parameters. It now requires a **JSON Request Body** and includes strict player name uniqueness validation.

### HTTP Request Format
You must send a `POST` request with the following JSON payload data (`Content-Type: application/json`):

```json
{
  "session_code": "1234",
  "player_name": "Frank"
}
```

### Expected Callbacks & Errors
The frontend must be prepared to catch specific HTTP exceptions thrown by the backend router.

* **Success (200 OK)**: Name is unique and player is successfully added.
```json
{
    "status": "success",
    "message": "Player Frank successfully joined session 1234",
    "player_token": "placeholder_token_123"
}
```

* **Validation Error (HTTP 400 Bad Request)**: 
If the user tries to join with a name that is already currently active in the session (e.g., "Alice"), the backend blocks the connection. The frontend needs to catch this error and display a UI warning preventing them from moving to the game room.
```json
{
    "detail": "The name 'Alice' is already taken in this session. Please choose another one."
}
```

### Action Items for Frontend
1. Update the `.fetch()` or `axios` calls pointing to `/api/connect` to pass the user's input as `JSON.stringify()`.
2. Implement a `try...catch` block on the Join page. If `res.status === 400`, display the returned `detail` message directly under the Player Name input box.
