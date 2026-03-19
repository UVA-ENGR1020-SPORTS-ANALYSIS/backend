# Data Rules

## 1. Player Info
To save or look up a player, we use this naming rule:
`player:ID_NUMBER`

*What to save for them:*
* Name
* Team
* Total Points
* Total Assists

## 2. The Live Game
To update the current score, we use this naming rule:
`game:live`

*What to save here:*
* Game Session ID
* Home Score
* Away Score
* Which team currently has the ball

## 3. Shot History
To keep a running list of every shot taken, we use this naming rule:
`game:shot_log`

*What to save here (as a running list):*
* Game Session ID
* Player ID (Who shot it)
* Player Team
* Did it go in? (True/False)
* Score Type (1, 2, or 3 points)
* Scored Area (e.g., "area#1")
* X Coordinate
* Y Coordinate