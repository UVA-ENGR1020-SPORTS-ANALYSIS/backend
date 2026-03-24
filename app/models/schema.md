# Data Rules (Supabase Schema Design)

## 1. Team Info
To organize players into squads, we use this naming rule `team:ID_NUMBER`.

*What to save for them (Table: teams):*
* Team ID (Primary Key)
* Team Name
* Total Wins
* Total Losses
* Roster (Players associated with this team)

## 2. Player Info
To save or look up a player, we use this naming rule `player:ID_NUMBER`.

*What to save for them (Table: players):*
* Player ID (Primary Key)
* Name
* Jersey Number (Crucial for fast live game logging)
* Team ID (Foreign Key linking to Team Info)
* Total Points
* Total Assists
* Total Rebounds (For deep analysis)
* Total Steals (For deep analysis)

## 3. The Live Game (Game Sessions)
To update the current score and manage a match, we use this naming rule `game:session_ID`.

*What to save here (Table: games):*
* Game Session ID (Primary Key)
* Home Team ID
* Away Team ID
* Home Score
* Away Score
* Current Possession (Which team currently has the ball)
* Status (e.g., "waiting", "in_progress", "completed")
* Created At / Ended At (Timestamps)

## 4. Shot History (Play-by-Play Log)
To keep a running list of every shot taken for later fetching and drawing shot charts, we use this naming rule `game:shot_log`.

*What to save here (Table: shot_log):*
* Shot ID (Primary Key, unique for every single shot)
* Game Session ID (Which game this happened in)
* Player ID (Who shot it)
* Team ID (Which team took the shot)
* Did it go in? (True/False)
* Score Type (1, 2, or 3 points)
* Shot Type (Optional: Jump Shot, Layup, Free Throw, etc.)
* Scored Area (e.g., "area#1")
* X Coordinate
* Y Coordinate
* Timestamp / Game Clock (Exactly when the shot was taken)