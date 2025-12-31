-- 4. Resource Production/Consumption (weeklyreport_coin)
-- ==================================================================
-- Description: Production and Consumption of resources separated by VIP and Zone (10001-39001).
select a.day,vip,a_typ,type,coin_typ,count(distinct a.mbga_uid,a.user_id) uu,sum(amount) amount from
(
    select day,mbga_uid,user_id,case when diff<0 then '消费' when diff>0 then '产出' end as type,
    case when obj in ('dmp:stamps','dmp:freestamps') then 'stamps' else split(obj,':|@')[1] end as coin_typ,a_typ,sum(abs(cast(diff as int))) as amount
    from g33002013.daily_game_log
    LATERAL VIEW explode(a_rst) rst_tab as rst
    LATERAL VIEW json_tuple(rst,'obj','diff') j_tab as obj,diff
    where day>={day15}
    and split(obj,':|@')[1] in ('stamps','freestamps','money','gold')
    and diff <> 0
    and zone between 'ali_tt_10001' and 'ali_tt_39001'
    and a_typ not in ('gacha_buy')
    group by mbga_uid,user_id,case when diff < 0 then '消费' when diff > 0 then '产出' end,
    case when obj in ('dmp:stamps','dmp:freestamps') then 'stamps' else split(obj,':|@')[1] end,a_typ,day
) a 
left join
(
    select day,mbga_uid,user_id,case when total_pay=0 then 'V0'
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
) b on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id and a.day=b.day
left join (select distinct mbga_uid from g33002013.user_blacklist) bl
on a.mbga_uid=bl.mbga_uid where bl.mbga_uid is null 
group by vip,type,coin_typ,a_typ,a.day;

-- ==================================================================