-- 1. Example OP User Log (user_day_log)
-- Description: Query a user's log for a specific day.

SELECT *
FROM g65002007.daily_game_log -- Replace with actual table name
WHERE role_id = '{role_id}'
  AND day = '{day}'
LIMIT 100;
