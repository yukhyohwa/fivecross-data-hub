-- 10. Player (Card) Development (weeklyreport_carddevelop)
-- ==================================================================
-- Description: Player card ownership, level, and grade distribution by VIP.
select a.vip,all_uu,card_id,get_uu,grade,level,D_GRADE,C_GRADE,B_GRADE,A_GRADE,S_GRADE
from
(
    select vip,count(distinct a.mbga_uid,a.user_id) all_uu
    from
    (
        select distinct get_json_object(value,'$.roleId') user_id,lid as mbga_uid,concat('ali_tt_',get_json_object(value,'$.zoneId')) as zone
        from g33002013.user_event
        where day>={day7}
    ) a
    left join
    (
        select mbga_uid,user_id,match_rank,'1' as a1,case when total_pay=0 then 'V0'
        when total_pay between 1 and 1200 then 'V1'
        when total_pay between 1201 and 5900 then 'V2'
        when total_pay between 5901 and 20000 then 'V3'
        when total_pay between 20001 and 80000 then 'V4'
        when total_pay between 80001 and 170000 then 'V5'
        when total_pay between 170001 and 500000 then 'V6'
        when total_pay between 500001 and 1700000 then 'V7'
        when total_pay >= 1700001 then 'V8' end as vip
        from
        (
            select *
            from g33002013.daily_user_snapshot where day={day1}
        ) a
    ) b on a.user_id=b.user_id and a.mbga_uid=b.mbga_uid
    left join g33002013.user_blacklist e on a.mbga_uid=e.mbga_uid
    where e.mbga_uid is null
    group by vip
) a 
left join
(
    select vip,card_id,count(distinct a.mbga_uid,a.user_id) get_uu,sum(grade) grade,sum(level) level,
    count(distinct case when grade=1 then a.user_id else null end) as D_GRADE,
    count(distinct case when grade=2 then a.user_id else null end) as C_GRADE,
    count(distinct case when grade=3 then a.user_id else null end) as B_GRADE,
    count(distinct case when grade=4 then a.user_id else null end) as A_GRADE,
    count(distinct case when grade=5 then a.user_id else null end) as S_GRADE,avg(honor) honor
    from
    (
        select distinct get_json_object(value,'$.roleId') user_id,lid as mbga_uid
        from g33002013.user_event
        where day>={day7}
    ) a
    left join
    (
        select mbga_uid,user_id,match_rank,'1' as a1,case when total_pay=0 then 'V0'
        when total_pay between 1 and 1200 then 'V1'
        when total_pay between 1201 and 5900 then 'V2'
        when total_pay between 5901 and 20000 then 'V3'
        when total_pay between 20001 and 80000 then 'V4'
        when total_pay between 80001 and 170000 then 'V5'
        when total_pay between 170001 and 500000 then 'V6'
        when total_pay between 500001 and 1700000 then 'V7'
        when total_pay >= 1700001 then 'V8' end as vip
        from 
        (
            select *
            from g33002013.daily_user_snapshot where day={day1}
        ) a
    ) b on a.user_id=b.user_id and a.mbga_uid=b.mbga_uid
    left join
    (
        select mbga_uid,user_id,card_id,grade,level,user_card_id,get_json_object(extra_info,'$.honor') honor
        from 
        (
            select *
            from g33002013.daily_user_card_snapshot where day={day1}
        ) a where status='1'
    ) c
    on a.mbga_uid=c.mbga_uid and a.user_id=c.user_id
    left join (select *,'1' as a1 from g33002013.dim_rank) d on b.a1=d.a1
    left join g33002013.user_blacklist e on a.mbga_uid=e.mbga_uid
    where b.match_rank>=d.min_star and b.match_rank<=d.max_star and e.mbga_uid is null
    group by vip,card_id
) b
on a.vip=b.vip;

-- ==================================================================