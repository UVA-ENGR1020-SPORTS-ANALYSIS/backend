# Backend — Tabletop Basketball

FastAPI backend for the Tabletop Basketball app. Manages game sessions, teams, players, and shot tracking via Supabase (PostgreSQL).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Create a `.env` file from `env.example` with your Supabase credentials.
Set `ADMIN_API_KEY` and send it as `X-Admin-Key` for admin-only session and player mutation endpoints.

## Project Structure

```
app/
├── main.py                  # FastAPI app, CORS, router registration
├── config.py                # Environment config (PORT, etc.)
├── models/
│   ├── player.py            # Player Pydantic model
│   └── schemas.py           # Request/response schemas with validation
├── routes/
│   ├── connect.py           # Session joining & lobby flow
│   ├── sessions.py          # Session CRUD
│   ├── game.py              # Shot submission & game progression
│   └── players.py           # Player stats & updates
└── supabase_wrapper/
    ├── client.py             # Supabase client singleton
    ├── sessions.py           # Session DB queries
    ├── teams.py              # Team DB queries
    ├── players.py            # Player DB queries & stats
    └── shots.py              # Shot recording & team stats
```

## API Endpoints

### Connect — `/api/connect`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/{session_code}` | Validate a room code exists and has space |
| `POST` | `/` | Join a session as a team (bulk-creates players) |
| `POST` | `/{team_id}/ready` | Toggle a team's ready status |

### Sessions — `/api/sessions`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/` | Create a new game session (returns 6-digit code) |
| `GET` | `/` | List sessions (admin-only, sanitized fields) |
| `GET` | `/{session_code}` | Get session details with teams & players |
| `DELETE` | `/{session_id}` | End a session (admin-only soft-delete, sets status to `ended`) |

### Game — `/api/game`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/shot` | Record a shot (updates player & team stats) |
| `POST` | `/finish_round` | Mark a team as done with round 1 or 2 |
| `GET` | `/team_stats/{team_id}/{round_number}` | Get a team's shots & points for a round |
| `GET` | `/opponent_stats/{session_id}/{my_team_id}` | Poll opponent's round 1 completion & stats |
| `POST` | `/ban` | Ban a zone for the opponent in round 2 |

### Players — `/api/players`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/team/{team_id}` | Get all players & stats for a team |
| `GET` | `/{player_id}` | Get a single player's stats |
| `POST` | `/` | Create a player |
| `PUT` | `/{player_id}` | Update a player's name (admin-only) |

## Database Schema (Supabase)

| Table | Key Columns |
|-------|-------------|
| `sessions` | `session_id`, `session_code`, `status`, `target_team` |
| `teams` | `team_id`, `current_session`, `is_ready`, `round_1_finished`, `round_2_finished`, `banned_zone` |
| `player` | `player_id`, `player_team_id`, `player_name`, `total_points`, `total_makes`, `total_attempts`, `shooting_pct` |
| `shots` | `shot_id`, `shot_player_id`, `team_id`, `session_id`, `zone`, `shot_made`, `round_number`, `points` |

RLS is enabled on all tables.

## Game Flow

1. **Create** → Host creates a session, gets a 6-digit code
2. **Join** → Teams join via code, register player names
3. **Lobby** → Teams toggle ready; game starts when all ready
4. **Round 1** → Each player takes 5 shots across 6 zones
5. **Results** → View per-player stats & zone heatmap
6. **Ban Phase** → (Multi-team) Ban one of opponent's zones
7. **Round 2** → Shoot again, banned zone is blocked
8. **Final** → Compare round 2 scores, declare winner
