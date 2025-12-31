-- 2. Recharge Tiers (weeklyreport_paidrank)
-- ==================================================================
-- Description: Daily active users and sales by recharge tier.
select a.day,sales_typ,all_uu,uu,sales
from
(
    select day,count(distinct lid) all_uu
    from g33002013.active_user_info
    where day>={day15}
    group by day
) a
left join
(
    select day,split(memo1,',')[1] as sales_typ,count(distinct lid) uu,sum(paid_lnum) sales
    from g33002013.consume_vc
    where day >={day15}
    and paid_lnum>0
    group by day,split(memo1,',')[1]
) b
on a.day=b.day;

-- ==================================================================