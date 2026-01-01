-- 1. VIP Distribution (weeklyreport_vip)
-- ==================================================================
-- Description: Daily VIP level distribution count.
SELECT b.day,vip,count(DISTINCT  a.mbga_uid,a.user_id)
FROM
(
    SELECT *
    from g33002013.daily_vip
    where day>={day15}
) a
left JOIN 
(
    select distinct get_json_object(value,'$.roleId') user_id,lid as mbga_uid,day
    from g33002013.user_event 
    where day>={day15}
) b on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id and a.day=b.day
GROUP  by b.day,vip;

-- ==================================================================