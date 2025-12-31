-- 13. Shop Purchases (weeklyreport_shopbuy)
-- ==================================================================
-- Description: Items bought in shop categorized by shop ID, item, currency, VIP.
select a.vip,all_uu,shop,a.item_id,coin_typ,uu,amount,num
from
(
    select vip,item_id,count(distinct a.mbga_uid,a.user_id) all_uu
    from
    (
        select distinct day,get_json_object(value,'$.roleId') user_id,lid as mbga_uid
        from g33002013.user_event 
        where day between {day7} and {day1}
    ) a join
    (select * from g33002013.daily_vip where day={day1}) b
    on a.user_id=b.user_id and a.mbga_uid=b.mbga_uid
    join
    (
        select distinct get_json_object(a_tar,'$.item_id') item_id,day
        from g33002013.daily_game_log
        where day between {day7} and {day1}
        and a_typ = 'shop_buy'
    ) c on a.day=c.day
    group by vip,item_id
) a
left join
(
    select vip,shop,item_id,coin_typ,count(distinct a.user_id,a.mbga_uid) uu,sum(a.amount) amount,sum(a.num) num
    from
    (
        select get_json_object(a_tar,'$.shop_id') shop,get_json_object(a_tar,'$.item_id') item_id,
        case when obj in ('dmp:stamps','dmp:freestamps') then 'stamps' else split(obj,':|@')[1] end as coin_typ
        ,log_t,user_id,mbga_uid,-diff as amount,get_json_object(a_tar,'$.num') as num
        from g33002013.daily_game_log
        LATERAL VIEW explode(a_rst) rst_tab as rst
        LATERAL VIEW json_tuple(rst,'obj','diff') j_tab as obj,diff 
        where day between {day7} and {day1}
        and a_typ in ('shop_buy')
        and diff<0
    ) a join (select * from g33002013.daily_vip where day={day1}) b
    on a.user_id=b.user_id and a.mbga_uid=b.mbga_uid
    left join (select distinct mbga_uid from g33002013.user_blacklist) bl
    on a.mbga_uid=bl.mbga_uid 
    where bl.mbga_uid is null 
    group by vip,shop,item_id,coin_typ
) b
on a.vip=b.vip and a.item_id=b.item_id;

-- ==================================================================