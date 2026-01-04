-- 9. Match Participation by Rank (weeklyreport_matchrank)
-- Description: Match stats broken down by player's rank.
-- Description: Match stats broken down by player's rank.
SELECT a.day, c.name AS type, rank_name, 
       COUNT(DISTINCT a.mbga_uid, a.user_id) AS uu, 
       COUNT(DISTINCT a.mbga_uid, a.session) AS matchs, 
       SUM(match_time) AS match_time,
       COUNT(DISTINCT CASE WHEN a.result = 'true' THEN CONCAT(a.mbga_uid, a.session) ELSE NULL END) AS win,
       COUNT(DISTINCT CASE WHEN a.result <> b.result AND b.players <> 0 THEN CONCAT(a.mbga_uid, a.session) ELSE NULL END) AS pvp_times,
       COUNT(DISTINCT CASE WHEN a.result = 'true' AND a.result <> b.result AND b.players <> 0 THEN CONCAT(a.mbga_uid, a.session) ELSE NULL END) AS pvp_win
FROM (
    SELECT day, mbga_uid, user_id, session, type, match_time, SPLIT(star, '#')[0] AS star, result, '1' AS a1
    FROM g33002013.daily_match_snapshot
    WHERE day >= {day15} AND ai = 'false'
) a
LEFT JOIN (SELECT *, '1' AS a1 FROM g33002013.dim_rank) d ON a.a1 = d.a1
LEFT JOIN g33002013.dim_match c ON a.type = c.id
LEFT JOIN (
    SELECT session, result, COUNT(DISTINCT CASE WHEN ai = 'false' THEN user_id ELSE NULL END) AS players
    FROM g33002013.daily_match_snapshot
    WHERE day >= {day15}
    GROUP BY session, result
) b ON a.session = b.session
LEFT JOIN g33002013.user_blacklist e ON a.mbga_uid = e.mbga_uid
WHERE a.star >= d.min_star AND a.star <= d.max_star AND e.mbga_uid IS NULL
GROUP BY a.day, c.name, rank_name;

