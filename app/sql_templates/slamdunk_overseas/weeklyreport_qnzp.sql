-- 15. Roulette/Gacha Spin (weeklyreport_qnzp)
-- ==================================================================
-- Description: Gacha (proficiency_gacha, roulette_buy) participation by VIP.
select a.day,a.vip,all_uu,a_typ,uu,times
from
(
    select day,case when total_pay=0 then 'V0'
    when total_pay between 1 and 1200 then 'V1'
    when total_pay between 1201 and 5900 then 'V2'
    when total_pay between 5901 and 20000 then 'V3'
    when total_pay between 20001 and 80000 then 'V4'
    when total_pay between 80001 and 170000 then 'V5'
    when total_pay between 170001 and 500000 then 'V6'
    when total_pay between 500001 and 1700000 then 'V7'
    when total_pay >= 1700001 then 'V8' end as vip,count(distinct user_id) all_uu
    from g33002013.daily_user_snapshot t where day>={day15}
    group by day,case when total_pay=0 then 'V0'
    when total_pay between 1 and 1200 then 'V1'
    when total_pay between 1201 and 5900 then 'V2'
    when total_pay between 5901 and 20000 then 'V3'
    when total_pay between 20001 and 80000 then 'V4'
    when total_pay between 80001 and 170000 then 'V5'
    when total_pay between 170001 and 500000 then 'V6'
    when total_pay between 500001 and 1700000 then 'V7'
    when total_pay >= 1700001 then 'V8' end
) a
left join
(
    select b.vip,a.a_typ,count(distinct a.mbga_uid) uu,sum(times) times,a.day
    from
    (
        SELECT  day,mbga_uid,user_id,a_typ,sum(GET_JSON_OBJECT(a_tar,'$.times')) times
        from g33002013.daily_game_log where day>={day15}
        and a_typ in ('proficiency_gacha','roulette_buy') 
        group by mbga_uid,user_id,a_typ,day
    ) a 
    left join (select t.*,case when total_pay=0 then 'V0'
    when total_pay between 1 and 1200 then 'V1'
    when total_pay between 1201 and 5900 then 'V2'
    when total_pay between 5901 and 20000 then 'V3'
    when total_pay between 20001 and 80000 then 'V4'
    when total_pay between 80001 and 170000 then 'V5'
    when total_pay between 170001 and 500000 then 'V6'
    when total_pay between 500001 and 1700000 then 'V7'
    when total_pay >= 1700001 then 'V8' end as vip
    from g33002013.daily_user_snapshot t where day>={day15}) b
    on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id and a.day = b.day
    group by b.vip,a.a_typ,a.day
) b
on a.day=b.day and a.vip=b.vip;

-- ==================================================================