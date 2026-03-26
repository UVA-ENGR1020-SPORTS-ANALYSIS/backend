# Database Schema: Core Shot Tracker

## 1. Table: `sessions`
| Column | Data Type | Description |
| :--- | :--- | :--- |
| **session_id** | uuid (PK) | Primary key for the session. |
| **session_code** | int4 | Integer session code (Must be exactly 6 digits). |

## 2. Table: `teams`
| Column | Data Type | Description |
| :--- | :--- | :--- |
| **team_id** | uuid (PK) | Primary key for the team. |
| **current_session** | uuid (FK) | Foreign key linking to `sessions.session_id`. |

## 3. Table: `player`
| Column | Data Type | Description |
| :--- | :--- | :--- |
| **player_id** | uuid (PK) | Primary key for the player. |
| **player_team_id** | uuid (FK) | Foreign key linking to `teams.team_id`. |

## 4. Table: `shots`
| Column | Data Type | Description |
| :--- | :--- | :--- |
| **shot_id** | uuid (PK) | Primary key for the shot. |
| **shot_player_id** | uuid (FK) | Foreign key linking to `player.player_id`. |
| **shot_made** | boolean | True/False for make or miss. |
| **zone** | int4 | Integer representing the shot zone (Must be 1 through 6). |