# Game Phase Implementation Plan

This plan outlines the architecture for the Game Phase of the Sports Analysis App. We will implement support for both Single Team (1 round) and Multi-Team (2 rounds with banning) modes. 

## Proposed Changes

### 1. Database Schema Additions (Supabase)

To support the spreadsheet structure you requested and track game states during rounds, we need to modify our existing tables.

#### `shots` table (Store individual shot records)
This matches your required spreadsheet completely.
*   **`shot_id`**: UUID (Primary Key)
*   **`created_at`**: Timestamptz (Default: `now()`) -> *Corresponds to "Timestamp"*
*   **`session_id`**: UUID (Foreign Key to `sessions`) -> *For easier holistic querying*
*   **`team_id`**: UUID (Foreign Key to `teams`)
*   **`player_id`**: UUID (Foreign Key to `players`) -> *Corresponds to "Player"*
*   **`round_number`**: Integer (1 or 2)
*   **`location` / `zone`**: Integer (1-6) -> *Corresponds to "Location"*
*   **`is_make`**: Boolean -> *Corresponds to "Make?"*
*   **`make_value`**: Integer (1 for yes, 0 for no)
*   **`location_value`**: Integer (e.g., 2 or 3 depending on zone)
*   **`points`**: Integer (`make_value` * `location_value`) -> *Corresponds to "Points"*

#### `teams` table (Track team-specific game progress)
*   [NEW] **`round_1_finished`**: Boolean (Default: false) -> *Track who is done with 5 shots*
*   [NEW] **`round_2_finished`**: Boolean (Default: false)
*   [NEW] **`banned_zone`**: Integer (Default: null) -> *Store the zone that the opponent banned this team from shooting in during round 2*

---

### 2. Backend Routes (`backend/app/routes/game.py`)

#### [NEW] `POST /api/game/shot`
*   **Purpose**: Submit a new shot.
*   **Logic**: Records the shot into the `shots` table. Automatically calculates `make_value`, `location_value`, and `points` based on standard rules if the frontend doesn't provide them. Updates the team's total score.
*   **Validation**: Each player max 5 shots per round. Check if they shot in a `banned_zone` (reject if so).

#### [NEW] `POST /api/game/finish_round`
*   **Purpose**: Flag that a team has finished their 5 shots for the current round. 
*   **Logic**: Updates `round_1_finished` or `round_2_finished` for a team.

#### [NEW] `GET /api/game/opponent_stats/{session_id}/{my_team_id}`
*   **Purpose**: After round 1, fetch the opponent's round 1 data to display on the banning page.

#### [NEW] `POST /api/game/ban`
*   **Purpose**: Submit a zone ban for the opponent.
*   **Logic**: Takes an `opponent_team_id` and `zone_to_ban`, then updates the opponent's `banned_zone` in the `teams` table.

---

### 3. Frontend Architecture (`frontend/src/routes/GamePage.tsx`)

#### State Management
*   **`currentRound`**: Number (1 or 2).
*   **`phase`**: Enum (`SHOOTING`, `WAITING_FOR_OPPONENT`, `BANNING`, `FINISHED`).
*   **`selectedPlayerId`**: UUID (Track the player currently selected sideways to make the shot).

#### Components
*   **`HalfCourt`**: An interactive SVG/CSS based half basketball court divided into 6 clickable location zones.
*   **`PlayerList`**: Sidebar showing players in the current team. Clicking a player makes them the "Active Shooter". Shows remaining shots (X/5) per player.
*   **`MakeMissDialog`**: A modal/tooltip that pops up instantly after clicking a zone on the court, asking "Did the player MAKE or MISS?".
*   **`BanOpponentModal`**: Renders the opponent's stats from Round 1 and lets the user select one zone to ban.

#### Flow
1. **Init**: Load players for current team. Start `SHOOTING` phase (Round 1).
2. **Shooting Logic**: User clicks Player -> User clicks Zone -> User selects Make/Miss -> API Call to `/api/game/shot`.
3. **End Round 1**: After 5 shots per player, call `/api/game/finish_round`.
4. **Transition**: 
   * If Single Team -> Jump to Stats/Result Page.
   * If Multi Team -> Wait via Poll until opponent also finishes Round 1 -> Enter `BANNING` phase.
5. **Banning**: View opponent stats, submit a ban for them. Wait until opponent bans us.
6. **Round 2**: Reset counters. Zones banned by opponent are unclickable/grayed out. Shoot 5 times per player.
7. **End**: Jump to Stats/Result Page.

## Open Questions

> [!WARNING] Point Values & Locations
> What are the exact points associated with each of the 6 zones? E.g., which zones are worth 3 points vs 2 points?

> [!IMPORTANT] Per-Player Shot Limits
> You mentioned "each player five shots". Does this mean EVERY player in a team MUST individually take exactly 5 shots per round? If a team has 3 players, are there 15 shots total in Round 1?

> [!WARNING] Ban Mode Mechanic
> Does the opponent's ban "remove" that zone visually from your court, meaning you are literally not allowed to select that zone anymore for Round 2?

## Verification Plan

### Database & Backend
- Connect to Supabase and implement the schema columns natively.
- Run `/api/game/shot` via cURL to ensure `make_value`, `location_value`, and `points` auto-compute accurately.

### Frontend
- Emulate the HalfCourt component clicks.
- Mock an opponent's state progression to verify the transition to the banning phase.
