-- 14. Potential/Proficiency Level (weeklyreport_proficiency)
-- ==================================================================
-- Description: Top 3 Proficiency Plans levels for users by VIP.
select vip,
count(distinct a.user_id,a.mbga_uid) all_uu,
count(distinct b.mbga_uid,plan) plan_num,
sum(case when row=1 then lv else 0 end) as plan1,
sum(case when row=2 then lv else 0 end) as plan2,
sum(case when row=3 then lv else 0 end) as plan3
from
(
    select mbga_uid,user_id,plan,lv,
    row_number()over(partition by mbga_uid,user_id order by lv desc) as row
    from
    (
        select mbga_uid,user_id,plan
        ,sum( substr(item_id,4,1) ) lv
        from g33002013.daily_user_proficiency_snapshot
            where day ={day1} and (aindex < 22 or aindex > 24)
        group by mbga_uid,user_id,plan
    ) a
) a
join
(
    select * from g33002013.daily_vip where day={day1}
) b on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id
join
(
    select distinct get_json_object(value,'$.roleId') user_id,lid as mbga_uid
    from g33002013.user_event 
    where day between {day7} and {day1}
) c on a.mbga_uid=c.mbga_uid and a.user_id=c.user_id
group by vip;

-- ==================================================================