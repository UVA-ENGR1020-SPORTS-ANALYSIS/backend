# Game Phase Implementation Overview

The logic for the main basketball game phase in both single and multiplayer modes is now implemented! Here is a summary of how the architecture was built based on your requirements.

## 1. Database Adjustments (Schema)

To accurately store data exactly like your spreadsheet (`Timestamp`, `Player`, `Location`, `Make?`, `Make Value`, `Location Value`, `Points`), I have provided an SQL script at `backend/migration.sql`.

> [!IMPORTANT]
> **Action Required**: You MUST go to your Supabase web dashboard, open the SQL Editor, and paste/run the contents of the `migration.sql` file. This is crucial because it adds the necessary columns to track `round_number`, `points`, and the `banned_zone` for multiplayer logic.

## 2. Backend Routing (`app/routes/game.py`)

I added robust REST endpoints to handle the transition between states smoothly:
- **`POST /api/game/shot`**: Stores the raw shot data in Supabase. It automatically calculates `points` by multiplying the `make_value` (0 or 1) by a mapped `location_value` standard to basketball.
- **`POST /api/game/finish_round`**: Registers that a team has finished their 5 shots for the current round.
- **`GET /api/game/opponent_stats/...`**: Allows a team to poll the logic gateway to see if their opponent has finished Round 1, fetching their score required for the "Banning" phase.
- **`POST /api/game/ban`**: Stores the choice of a banned zone onto the opponent's team record essentially locking them out in Round 2.

## 3. Frontend Architecture

### Visual Half Court Component
I built an SVG based interactive `<HalfCourt />` component in `frontend/src/components/HalfCourt.tsx`. Because CSS/HTML layouts don't map well to organic physical spaces, an SVG maps exact vectors so users can intuitively tap where they shot. 

### Core Game Logic (`GamePage.tsx`)
The `GamePage` works as a heavy state machine governing the rules you established:
1. **Roster Tracking**: It queries the active players and ensures no player can shoot more than exactly 5 times.
2. **Shot Dialog**: Triggered instantly when someone taps the `<HalfCourt />` it asks "Make or Miss", then dispatches to the backend APIs.
3. **Wait & Ban UI**: If multiplayer, once all players reach 5 shots it transitions into a real-time waiting screen. Once the opponent finishes, the user is presented a prominent Ban screen showing the opponent's Round 1 points and asks the user to pick a zone to ban.
4. **Round 2 Initialization**: Once a ban is selected, the game restarts into Round 2—resetting the player counters. The banned zone is passed to the `<HalfCourt />` showing up as grayed-out and permanently disabled for interactions.

### Assumptions Setup
- *Location Value / Points*: The system is currently mapped so that Zone 1 gives 1 point. Zones 2 and 3 give 2 points. Zones 4, 5, and 6 give 3 points. 
- *Shot Requirement*: The system counts down max 5 shots independently for each registered teammate.
- *Visual Ban*: Yes, during Round 2, the opponent's chosen ban will permanently lock & gray out that section on the local team's screen.
