-- 3. Currency Inventory (weeklyreport_paidremaind)
-- ==================================================================
-- Description: Daily stock of Stamps, Money, Gold, Match Coin by VIP level.
select a.day,vip,count(distinct a.mbga_uid,a.user_id),sum(stamps),sum(money),sum(gold),sum(match_coin)
from
(
    select distinct day,user_id,mbga_uid
    from g33002013.daily_game_log
    where day >={day15}
) a
join
(
    select day,user_id,mbga_uid,(stamps+free_stamps) as stamps,money,gold,match_coin,
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
    where day>={day15}
) b on a.user_id=b.user_id and a.mbga_uid=b.mbga_uid and a.day=b.day
group by a.day,vip;

-- ==================================================================