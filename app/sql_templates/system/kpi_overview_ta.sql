-- Index. KPI Overview (TA)
-- Description: Fetch high-level KPI data (MAU, NUU, Revenue) for TA-based games.

/*
  Note: This is a template for ThinkingData SQL.
  The schema depends on the actual event tables in TA.
  We assume standard event names like 'login', 'pay', etc. or a summary table.

  For compatibility with the dashboard, the output columns MUST be:
  app_id, app_name, region, obt_start_date, data_date, num_login_accounts_total, num_login_accounts_nuu, purchase
*/

SELECT
    '{game_id}' AS app_id,
    '{game_name}' AS app_name,
    'Global' AS region,
    '2024-01-01' AS obt_start_date, -- Placeholder or join with metadata
    DATE_FORMAT(time, '%Y-%m-%d') AS data_date,
    COUNT(DISTINCT IF(event_name = 'login', distinct_id, NULL)) AS num_login_accounts_total,
    COUNT(DISTINCT IF(event_name = 'register', distinct_id, NULL)) AS num_login_accounts_nuu,
    SUM(IF(event_name = 'pay', amount, 0)) AS purchase
FROM v_event
WHERE
    DATE_FORMAT(time, '%Y%m') BETWEEN '{start_month}' AND '{end_month}'
GROUP BY
    DATE_FORMAT(time, '%Y-%m-%d')
ORDER BY
    data_date
