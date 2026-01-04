-- Match Participation (weeklyreport_matchtype)
-- Description: Match stats (Times, Win, PvP vs AI) by match type.
SELECT all_uu, b.type, match_times, uu, times, win, pvp_uu, pvp_times, pvp_win, ping, a.day
FROM (
    SELECT day, COUNT(DISTINCT user_id, mbga_uid) AS all_uu
    FROM g33002013.daily_game_log
    WHERE day >= {day15}
    GROUP BY day
) a
LEFT JOIN (
    SELECT a.day, c.name AS type, COUNT(DISTINCT a.match_id) AS match_times,
           COUNT(DISTINCT a.mbga_uid) AS uu, COUNT(DISTINCT a.mbga_uid, log_t) AS times,
           COUNT(DISTINCT CASE WHEN reuslt = 'true' THEN CONCAT(a.mbga_uid, log_t) ELSE NULL END) AS win,
           COUNT(DISTINCT CASE WHEN AI_num < TAR_num THEN a.match_id ELSE NULL END) AS match_pvp_times,
           COUNT(DISTINCT CASE WHEN AI_num < TAR_num THEN a.mbga_uid ELSE NULL END) AS pvp_uu,
           COUNT(DISTINCT CASE WHEN AI_num < TAR_num THEN CONCAT(a.mbga_uid, log_t) ELSE NULL END) AS pvp_times,
           COUNT(DISTINCT CASE WHEN AI_num < TAR_num AND reuslt = 'true' THEN CONCAT(a.mbga_uid, log_t) ELSE NULL END) AS pvp_win
    FROM (
        SELECT day, get_json_object(a_tar, '$.type') AS type, get_json_object(a_tar, '$.match_id') AS match_id, mbga_uid, user_id, log_t, get_json_object(a_tar, '$.reuslt') AS reuslt
        FROM g33002013.daily_game_log
        WHERE day >= {day15}
          AND a_typ IN ('match_fight', 'arena_fight', 'com_fight', 'custom_fight')
        UNION ALL
        SELECT day, 'tower_fight' AS type, CONCAT(log_t, mbga_uid) AS match_id, mbga_uid, user_id, log_t, get_json_object(a_tar, '$.reuslt') AS reuslt
        FROM g33002013.daily_game_log
        WHERE day >= {day15}
          AND a_typ = 'tower_fight'
    ) a 
    LEFT JOIN (
        SELECT match_id, COUNT(DISTINCT CASE WHEN SUBSTR(teammate, 1, 2) = '23' THEN teammate ELSE NULL END) AS AI_num, COUNT(DISTINCT teammate) AS TAR_num
        FROM (
            SELECT DISTINCT day, match_id, REGEXP_REPLACE(teammate_id2, '\\[|\\]|"', '') AS teammate
            FROM (
                SELECT DISTINCT day, get_json_object(a_tar, '$.match_id') AS match_id, get_json_object(a_tar, '$.target_id') AS teammate_id
                FROM g33002013.daily_game_log
                WHERE day >= {day15}
                  AND a_typ IN ('match_fight', 'arena_fight', 'com_fight', 'custom_fight')
            ) a
            LATERAL VIEW explode(split(teammate_id, ',')) teammate AS teammate_id2
        ) a
        GROUP BY match_id
    ) b ON a.match_id = b.match_id
    LEFT JOIN g33002013.dim_match c ON a.type = c.id
    GROUP BY a.day, c.name
) b ON a.day = b.day
LEFT JOIN (
    SELECT a.day, name AS type, ping
    FROM (
        SELECT day, get_json_object(a_tar, '$.type') AS type, SUM(get_json_object(a_tar, '$.ping')) AS ping
        FROM g33002013.daily_game_log
        WHERE day >= {day15}
          AND a_typ = 'fight_data'
        GROUP BY day, get_json_object(a_tar, '$.type')
    ) a 
    LEFT JOIN g33002013.dim_match b ON a.type = b.id
) c ON b.day = c.day AND b.type = c.type
WHERE b.type IS NOT NULL;

