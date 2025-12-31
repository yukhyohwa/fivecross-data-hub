-- 12. Talent Usage (weeklyreport_talents)
-- ==================================================================
-- Description: Analysis of active talents (skills) by User VIP.
select a.*,b.skill1,uu
from
(
    select vip,card_id,count(distinct a.mbga_uid,a.user_id) get_uu
    from
    (
        select card_id,mbga_uid,user_id
        from g33002013.daily_user_card_snapshot
        where day ={day1} and status='1'
    ) a join
    (
        select mbga_uid,user_id,match_rank,'1' as a1,case when total_pay=0 then 'V0'
        when total_pay between 1 and 1200 then 'V1'
        when total_pay between 1201 and 5900 then 'V2'
        when total_pay between 5901 and 20000 then 'V3'
        when total_pay between 20001 and 80000 then 'V4'
        when total_pay between 80001 and 170000 then 'V5'
        when total_pay between 170001 and 500000 then 'V6'
        when total_pay between 500001 and 1700000 then 'V7'
        when total_pay >= 1700001 then 'V8' end  as vip
        from g33002013.daily_user_snapshot where day={day1}
        and to_char(from_unixtime(cast(last_login as int)),"yyyymmdd")>={day7}
    ) b on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id
    group by card_id,vip
) a
left join
(
    SELECT vip,card_id,skill1,count(DISTINCT a.mbga_uid,a.user_id) uu
    from
    (
        SELECT mbga_uid,user_id,card_id,skill1 from g33002013.daily_user_card_snapshot
        LATERAL VIEW explode(split(skill,',|\\\\[|\\\\]')) a_tar as skill1
        where day={day1}
        and length(skill1) BETWEEN 4 and 6
    ) a
    join
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
        from g33002013.daily_user_snapshot where day={day1}
        and to_char(from_unixtime(cast(last_login as int)),"yyyymmdd")>={day7}
    ) b on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id
    GROUP BY card_id,skill1,vip
) b
on a.card_id=b.card_id and a.vip=b.vip;

-- ==================================================================