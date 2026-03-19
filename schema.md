# Data Rules

## 1. Player Info
to save or look up a player, we use this naming rule: 
`player:ID_NUMBER`
*What to save for them:*
* Name
* Total Points
* Total Assists

## 2. The Live Game
to update the current score, we use this naming rule: 
`game:live`
*What to save here:*
* Home Score
* Away Score
* Which team currently has the ball

## 3. Shot History
to keep a running list of every shot taken, we use this naming rule: 
`game:shot_log`
*What to save here (as a running list):*
* Which player shot it
* Did it go in? (True/False)