-- Resource Production/Consumption (weeklyreport_coin)
-- Description: Production and Consumption of resources separated by VIP and Zone (10001-39001).
SELECT a.day, vip, a_typ, type, coin_typ, COUNT(DISTINCT a.mbga_uid, a.user_id) AS uu, SUM(amount) AS amount
FROM (
    SELECT day, mbga_uid, user_id,
           CASE WHEN diff < 0 THEN '消费' WHEN diff > 0 THEN '产出' END AS type,
           CASE WHEN obj IN ('dmp:stamps', 'dmp:freestamps') THEN 'stamps' ELSE SPLIT(obj, ':|@')[1] END AS coin_typ,
           a_typ, SUM(ABS(CAST(diff AS INT))) AS amount
    FROM g33002013.daily_game_log
    LATERAL VIEW explode(a_rst) rst_tab AS rst
    LATERAL VIEW json_tuple(rst, 'obj', 'diff') j_tab AS obj, diff
    WHERE day >= {day15}
      AND SPLIT(obj, ':|@')[1] IN ('stamps', 'freestamps', 'money', 'gold')
      AND diff <> 0
      AND zone BETWEEN 'ali_tt_10001' AND 'ali_tt_39001'
      AND a_typ NOT IN ('gacha_buy')
    GROUP BY mbga_uid, user_id,
             CASE WHEN diff < 0 THEN '消费' WHEN diff > 0 THEN '产出' END,
             CASE WHEN obj IN ('dmp:stamps', 'dmp:freestamps') THEN 'stamps' ELSE SPLIT(obj, ':|@')[1] END,
             a_typ, day
) a 
LEFT JOIN (
    SELECT day, mbga_uid, user_id,
           CASE WHEN total_pay = 0 THEN 'V0'
                WHEN total_pay BETWEEN 1 AND 1200 THEN 'V1'
                WHEN total_pay BETWEEN 1201 AND 5900 THEN 'V2'
                WHEN total_pay BETWEEN 5901 AND 20000 THEN 'V3'
                WHEN total_pay BETWEEN 20001 AND 80000 THEN 'V4'
                WHEN total_pay BETWEEN 80001 AND 170000 THEN 'V5'
                WHEN total_pay BETWEEN 170001 AND 500000 THEN 'V6'
                WHEN total_pay BETWEEN 500001 AND 1700000 THEN 'V7'
                WHEN total_pay >= 1700001 THEN 'V8' END AS vip
    FROM g33002013.daily_user_snapshot
    WHERE day >= {day15}
) b ON a.mbga_uid = b.mbga_uid AND a.user_id = b.user_id AND a.day = b.day
LEFT JOIN (
    SELECT DISTINCT mbga_uid FROM g33002013.user_blacklist
) bl ON a.mbga_uid = bl.mbga_uid 
WHERE bl.mbga_uid IS NULL 
GROUP BY vip, type, coin_typ, a_typ, a.day;

