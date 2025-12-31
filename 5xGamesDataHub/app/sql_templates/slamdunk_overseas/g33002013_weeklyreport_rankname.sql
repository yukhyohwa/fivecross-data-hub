-- 8. Rank Distribution (weeklyreport_rankname)
-- ==================================================================
-- Description: User distribution by Rank Name (e.g., Bronze, Silver).
select rank_name,count(distinct a.mbga_uid,a.user_id) all_uu
from
(
    select distinct get_json_object(value,'$.roleId') user_id,lid as mbga_uid,concat('ali_tt_',get_json_object(value,'$.zoneId')) as zone
    from g33002013.user_event
    where day>={day7}
) a
left join
(
    select mbga_uid,user_id,match_rank,'1' as a1,case when total_pay=0 then 'V0' end as vip
    from
    (
        select *,row_number () over (partition by mbga_uid,user_id order by last_login desc) as rank 
        from g33002013.daily_user_snapshot where day={day1} and cast(level as int)>=8
    ) a where rank=1
) b on a.user_id=b.user_id and a.mbga_uid=b.mbga_uid
left join (select *,'1' as a1 from g33002013.dim_rank) d on b.a1=d.a1
left join g33002013.user_blacklist e on a.mbga_uid=e.mbga_uid
where b.match_rank>=d.min_star and b.match_rank<=d.max_star and e.mbga_uid is null
group by rank_name;

-- ==================================================================