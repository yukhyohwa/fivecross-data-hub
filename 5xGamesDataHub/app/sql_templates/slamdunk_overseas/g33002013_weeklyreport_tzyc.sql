-- 16. Trait Development (weeklyreport_tzyc)
-- ==================================================================
-- Description: Trait levels (Item ID suffix 4) distribution by VIP.
select a.*,b.all_uu
from
(
    SELECT vip,item_id,lv,count(distinct b.user_id) uu
    from 
    (
        select user_id,mbga_uid,cast(match_rank as int) match_rank,'1' as a1,
        case when total_pay=0 then 'V0'
        when total_pay between 1 and 1200 then 'V1'
        when total_pay between 1201 and 5900 then 'V2'
        when total_pay between 5901 and 20000 then 'V3'
        when total_pay between 20001 and 80000 then 'V4'
        when total_pay between 80001 and 170000 then 'V5'
        when total_pay between 170001 and 500000 then 'V6'
        when total_pay between 500001 and 1700000 then 'V7'
        when total_pay >= 1700001 then 'V8' end as vip
        from g33002013.daily_user_snapshot
        where day= {day1} and  to_char(from_unixtime(cast(last_login as int)),"yyyymmdd")>={day7}
    )a 
    left join
    (
        select substr(GET_JSON_OBJECT(a_tar,'$.item_id'),5,4) item_id,mbga_uid,user_id,
        max(substr(GET_JSON_OBJECT(a_tar,'$.item_id'),4,1)) lv
        from g33002013.daily_game_log 
        where day>=20200729 and a_typ in ('proficiency_decompose','proficiency_equip','proficiency_levelup')
        and substr(GET_JSON_OBJECT(a_tar,'$.item_id'),5,1)=4
        group by substr(GET_JSON_OBJECT(a_tar,'$.item_id'),5,4),mbga_uid,user_id
    ) b
    on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id
    group by vip,item_id,lv
) a
left join
(
    select case when total_pay=0 then 'V0'
    when total_pay between 1 and 1200 then 'V1'
    when total_pay between 1201 and 5900 then 'V2'
    when total_pay between 5901 and 20000 then 'V3'
    when total_pay between 20001 and 80000 then 'V4'
    when total_pay between 80001 and 170000 then 'V5'
    when total_pay between 170001 and 500000 then 'V6'
    when total_pay between 500001 and 1700000 then 'V7'
    when total_pay >= 1700001 then 'V8' end as vip,count(distinct user_id) all_uu
    from g33002013.daily_user_snapshot
    where day= {day1} and  to_char(from_unixtime(cast(last_login as int)),"yyyymmdd")>={day7}
    group by 
    case when total_pay=0 then 'V0'
    when total_pay between 1 and 1200 then 'V1'
    when total_pay between 1201 and 5900 then 'V2'
    when total_pay between 5901 and 20000 then 'V3'
    when total_pay between 20001 and 80000 then 'V4'
    when total_pay between 80001 and 170000 then 'V5'
    when total_pay between 170001 and 500000 then 'V6'
    when total_pay between 500001 and 1700000 then 'V7'
    when total_pay >= 1700001 then 'V8' end
) b
on a.vip=b.vip;