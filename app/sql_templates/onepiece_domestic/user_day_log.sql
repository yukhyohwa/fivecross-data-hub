-- 1. Example OP User Log (user_day_log)
-- Description: Query a user's log for a specific day.

SELECT *
FROM ods_log_table -- Replace with actual table name
WHERE role_id = '{role_id}'
  AND part_day = '{part_day}'
LIMIT 100;
