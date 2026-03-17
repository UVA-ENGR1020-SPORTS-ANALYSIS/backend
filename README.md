# backend
The backend for the sports data analysis app.

## Development Split
- **Developer 1 (Data):** Google Sheets API integration, Data Syncing, Data Cleaning.
- **Developer 2 (Backend):** Web Service setup, Analysis Logic, API Endpoints.

## Quick Start
1. `src/sheets/` - Data integration code.
2. `src/logic/` - Analysis and math code.
3. `main.py` - Web server entry point.


## sample return format:

```json
{
  "player_name": "player1",
  "team": "team1",
  "score type": "1/2/3points",
  "scored area": "area#1",
  "game session": "game session #1",
  "shooting coordinate": "x,y"   // for visualization
}
```

## Web service
- Web service (make sure the app can be accessed from the web)

