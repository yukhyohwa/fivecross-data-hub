-- Player (Card) Usage in Matches (weeklyreport_cards)
-- Description: Stats like WinRate, Score, Rebounds, Steals per player card in Ranked 3v3.
SELECT CASE WHEN pvp = 1 THEN '单机' WHEN pvp = 2 THEN 'PVP' END AS pvp_type,
       rank_name, d.name AS type, total_match, card_name AS player, match_times,
       get_player, win, score, twoN, twoG, layupN, layupG, dunkN, dunkG, 
       threeN, threeG, blockG, stealG AS stealG, rebG, asitN, mark, intercept, 
       groundN, ballT, twoN_open, twoG_open, threeN_open, threeG_open, downN, downND, a.day
FROM (
    SELECT a.day, pvp, rank_name, get_json_object(player, '$.player') AS player, type,
           COUNT(DISTINCT a.mbga_uid, a.session) AS match_times,
           COUNT(DISTINCT CASE WHEN get_json_object(player, '$.state') = '1' THEN CONCAT(a.mbga_uid, a.user_id) ELSE NULL END) AS get_player,
           COUNT(CASE WHEN result = 'true' THEN log_t ELSE NULL END) AS win,
           SUM(score) AS score,
           SUM(get_json_object(adata, '$.twoN')) AS twoN,
           SUM(get_json_object(adata, '$.twoG')) AS twoG,
           SUM(get_json_object(adata, '$.layupN')) AS layupN,
           SUM(get_json_object(adata, '$.layupG')) AS layupG,
           SUM(get_json_object(adata, '$.dunkN')) AS dunkN,
           SUM(get_json_object(adata, '$.dunkG')) AS dunkG,
           SUM(get_json_object(adata, '$.threeN')) AS threeN,
           SUM(get_json_object(adata, '$.threeG')) AS threeG,
           SUM(get_json_object(adata, '$.blockG')) AS blockG,
           SUM(get_json_object(adata, '$.stealG')) AS stealG,
           SUM(get_json_object(adata, '$.rebG')) AS rebG,
           SUM(get_json_object(adata, '$.asitN')) AS asitN,
           SUM(get_json_object(adata, '$.intercept')) AS intercept,
           SUM(get_json_object(adata, '$.ballT')) AS ballT,
           SUM(get_json_object(adata, '$.groundN')) AS groundN,
           SUM(get_json_object(player, '$.mark')) / 10000 AS mark,
           SUM(get_json_object(adata, '$.twoN_open')) AS twoN_open,
           SUM(get_json_object(adata, '$.twoG_open')) AS twoG_open,
           SUM(get_json_object(adata, '$.threeN_open')) AS threeN_open,
           SUM(get_json_object(adata, '$.threeG_open')) AS threeG_open,
           SUM(get_json_object(adata, '$.downN')) AS downN,
           SUM(get_json_object(adata, '$.downND')) AS downND
    FROM (
        SELECT player, mbga_uid, user_id, session, score, result, adata, CAST(SPLIT(star, '#')[0] AS INT) AS star, '1' AS a1, type, log_t, day
        FROM g33002013.daily_match_snapshot 
        WHERE day >= {day15}
          AND ai = 'false'
          AND type = 'RankH3V3'
    ) a 
    JOIN (
        SELECT DISTINCT user_id, mbga_uid, card_id, day
        FROM g33002013.daily_user_card_snapshot 
        WHERE day >= {day15} AND grade = 5
    ) e ON a.mbga_uid = e.mbga_uid AND a.user_id = e.user_id AND a.day = e.day AND get_json_object(a.player, '$.player') = e.card_id
    LEFT JOIN (SELECT *, '1' AS a1 FROM g33002013.dim_rank) d ON a.a1 = d.a1
    LEFT JOIN (
        SELECT session, COUNT(DISTINCT result) AS pvp
        FROM g33002013.match_snapshot 
        WHERE day >= {day15}
          AND ai = 'false'
        GROUP BY session
    ) b ON a.session = b.session
    WHERE a.star >= d.min_star AND a.star <= d.max_star
    GROUP BY a.day, pvp, get_json_object(player, '$.player'), type, rank_name
) a
LEFT JOIN (
    SELECT type, COUNT(DISTINCT mbga_uid, session) AS total_match
    FROM g33002013.match_snapshot 
    WHERE day >= {day15} AND ai = 'false'
    GROUP BY type
) c ON a.type = c.type
LEFT JOIN g33002013.dim_match d ON a.type = d.id
LEFT JOIN g33002013.dim_card_h5 e ON a.player = e.card_id
WHERE pvp = 2;

