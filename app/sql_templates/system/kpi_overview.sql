-- Index. KPI Overview
-- Description: Fetch high-level KPI data (MAU, NUU, Revenue) for all games.

SELECT a.app_id, 
    app_name, 
    region, 
    obt_start_date,
    data_date, 
    num_login_accounts_total,
    num_login_accounts_nuu,
    CAST(purchase AS DOUBLE) AS purchase
FROM
(
    SELECT CAST(app_id AS BIGINT) AS app_id, 
        SUBSTR(TO_DATE(month, 'yyyyMM'), 1, 10) AS data_date, 
        COUNT(DISTINCT lcm_id) AS num_login_accounts_total,
        COUNT(DISTINCT CASE WHEN user_type = 'nuu' THEN lcm_id ELSE NULL END) AS num_login_accounts_nuu,
        SUM(purchase) AS purchase
    FROM dm_platform.monthly_lcx_user_info
    WHERE month >= '{start_month}'
        AND month <= '{end_month}'
        AND is_water = '不是水'
    GROUP BY CAST(app_id AS BIGINT), SUBSTR(TO_DATE(month, 'yyyyMM'), 1, 10)
) a
INNER JOIN
(
    SELECT app_id, app_name, region, obt_start_date, NVL(obt_end_date, '2099-12-31') AS obt_end_date
    FROM dm_platform_dev.dim_app_info
    WHERE company = 'DeNA'
) b ON a.app_id = b.app_id
WHERE SUBSTR(data_date, 1, 7) >= SUBSTR(obt_start_date, 1, 7) AND SUBSTR(data_date, 1, 7) <= SUBSTR(obt_end_date, 1, 7)
ORDER BY app_id, data_date
