-- 5. Battle Pass Upgrade (weeklyreport_battlepassgrade)
-- ==================================================================
-- Description: Battle Pass level avg, users, and purchase stats by VIP.
select vip,count(distinct a.mbga_uid,a.user_id) all_uu,avg(b.level),count(distinct c.mbga_uid,c.user_id) buy_uu,sum(battlepass_buy) battlepass_buy,sum(battlepass_levelbuy) battlepass_levelbuy
from
(select * from g33002013.daily_vip where day={day1}) a
join
(
    select * from g33002013.daily_user_snapshot 
    where day={day1} 
    and to_char(from_unixtime(cast(last_login as int)),"yyyymmdd")>={initday}
) e
on a.mbga_uid=e.mbga_uid and a.user_id=e.user_id
left join
(
    SELECT mbga_uid,user_id,max(cast(regexp_replace(level,'\\\\[|\\\\]','') as int)) level
    from g33002013.daily_game_log
    LATERAL VIEW explode(split(GET_JSON_OBJECT(a_tar,'$.index'),',')) a_tar as level
    where day>={initday}
    and a_typ = 'battlepass_reward'
    group by mbga_uid,user_id
) b on a.mbga_uid=b.mbga_uid and a.user_id=b.user_id
left join
(
    select distinct mbga_uid,user_id
    from g33002013.daily_game_log
    where day>={initday} and a_typ='battlepass_buy'
) c on a.mbga_uid=c.mbga_uid and a.user_id=c.user_id
left join
(
    select mbga_uid,user_id,sum(case when a_typ='battlepass_buy' then abs(cast(diff as int)) else 0 end) as battlepass_buy,
    sum(case when a_typ='battlepass_levelbuy' then abs(cast(diff as int)) else 0 end) as battlepass_levelbuy
    from g33002013.daily_game_log
    LATERAL VIEW explode(a_rst) rst_tab as rst
    LATERAL VIEW json_tuple(rst,'obj','diff') j_tab as obj,diff
    where day>={initday}
    and split(obj,':|@')[1] in ('stamps','freestamps')
    and diff <> 0
    and a_typ in ('battlepass_buy','battlepass_levelbuy')
    group by mbga_uid,user_id
) d on a.mbga_uid=d.mbga_uid and a.user_id=d.user_id
group by vip
order by vip;

-- ==================================================================