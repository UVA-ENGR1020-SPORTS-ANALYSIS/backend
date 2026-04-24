# Backend — Tabletop Basketball

FastAPI backend for the Tabletop Basketball application. It manages game sessions, teams, players, and real-time shot tracking through Supabase (PostgreSQL).

## 🚀 Tech Stack

- **Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Validation:** Pydantic
- **Testing:** Pytest

## 📦 Setup & Running Locally

### 1. Virtual Environment

Create and activate a virtual environment:

```bash
# Create the virtual environment
python -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root of the `backend` directory based on the provided `env.example`:

```bash
cp env.example .env
```

Populate the `.env` file with your credentials:
```ini
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
WARMUP_KEY=any-random-secret-for-ping-checks
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

*Note: For admin-only session/player mutations, the server also expects an `ADMIN_API_KEY` in your environment, which must be sent as the `X-Admin-Key` header.*

### 4. Run the Server

Start the FastAPI backend with hot-reloading:

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000). You can view the interactive Swagger UI documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## 🧪 Testing

To run the unit and integration test suite, simply run:

```bash
pytest
```

## 📁 Project Structure

```
app/
├── main.py                  # FastAPI app, CORS, router registration
├── config.py                # Environment config loader
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

## 🌐 API Overview

- **Connect (`/api/connect`)**: Lobby creation and team readiness flow.
- **Sessions (`/api/sessions`)**: Admin tools to list, view, and soft-delete game sessions.
- **Game (`/api/game`)**: Core loop—submitting shots, finishing rounds, polling opponent status, and banning zones.
- **Players (`/api/players`)**: View and manage individual player statistics.

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| `sessions` | Tracks active, waiting, and ended game sessions. |
| `teams` | Tracks readiness, round progress, and banned zones for the opponent. |
| `player` | Stores player identity and aggregate shooting statistics. |
| `shots` | The primary append-only log of every shot taken in the game. |

RLS (Row Level Security) is enabled on all tables via Supabase.
