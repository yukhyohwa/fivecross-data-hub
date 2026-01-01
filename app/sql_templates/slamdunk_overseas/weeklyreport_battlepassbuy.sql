-- 6. Battle Pass Purchase (weeklyreport_battlepassbuy)
-- ==================================================================
-- Description: Battle Pass purchases (IDs 13220151, 13220150) by VIP.
select vip,count(distinct b.user_id),sum(sales) 
from
(select * from g33002013.daily_vip where day={day1}) a
join 
(
    select lid mbga_uid,split(memo1,',')[0] user_id,sum(paid_lnum) sales
    from g33002013.consume_vc
    where day >={initday} and split(memo1,',')[1] in (13220151,13220150)
    and paid_lnum>0
    group by lid,split(memo1,',')[0]
) b
on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id
group by vip
order by vip;

-- ==================================================================