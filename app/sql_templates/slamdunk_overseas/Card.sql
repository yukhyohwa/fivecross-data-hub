-- 11. Player (Card) Usage in Matches (weeklyreport_cards)
-- ==================================================================
-- Description: Stats like WinRate, Score, Rebounds, Steals per player card in Ranked 3v3.
select case when pvp=1 then '单机' when pvp=2 then 'PVP' end as pvp_type,rank_name,d.name type,total_match,card_name as player,match_times,
get_player,win,score,twoN,twoG,layupN,layupG,dunkN,dunkG,threeN,threeG,blockG,stealG as stealG,rebG,asitN,mark,intercept,groundN,ballT,twoN_open,twoG_open,threeN_open,threeG_open,downN,downND,a.day
from
(
    select a.day,pvp,rank_name,get_json_object(player,'$.player') player,type,count(distinct a.mbga_uid,a.session) match_times,
    count(distinct case when get_json_object(player,'$.state')='1' then concat(a.mbga_uid,a.user_id) else null end) get_player,
    count(case when result='true' then log_t else null end) win,sum(score) score,
    sum(get_json_object(adata,'$.twoN')) twoN,sum(get_json_object(adata,'$.twoG')) twoG,
    sum(get_json_object(adata,'$.layupN')) layupN,sum(get_json_object(adata,'$.layupG')) layupG,
    sum(get_json_object(adata,'$.dunkN')) dunkN,sum(get_json_object(adata,'$.dunkG')) dunkG,
    sum(get_json_object(adata,'$.threeN')) threeN,sum(get_json_object(adata,'$.threeG')) threeG,
    sum(get_json_object(adata,'$.blockG')) blockG,sum(get_json_object(adata,'$.stealG')) stealG,
    sum(get_json_object(adata,'$.rebG')) rebG,sum(get_json_object(adata,'$.asitN')) asitN,
    sum(get_json_object(adata,'$.intercept')) intercept,sum(get_json_object(adata,'$.ballT')) ballT,sum(get_json_object(adata,'$.groundN')) groundN,
    sum(get_json_object(player,'$.mark'))/10000 mark,sum(get_json_object(adata,'$.twoN_open')) twoN_open,sum(get_json_object(adata,'$.twoG_open')) twoG_open,
    sum(get_json_object(adata,'$.threeN_open')) threeN_open,sum(get_json_object(adata,'$.threeG_open')) threeG_open,
    sum(get_json_object(adata,'$.downN')) downN,sum(get_json_object(adata,'$.downND')) downND
    from
    (
        select player,mbga_uid,user_id,session,score,result,adata,cast(split(star,'#')[0] as int) star,'1' as a1,type,log_t,day
        from g33002013.daily_match_snapshot where day>={day15}
        and ai='false'
        and type='RankH3V3'
    ) a 
    join
    (
        select distinct user_id,mbga_uid,card_id,day
        from g33002013.daily_user_card_snapshot where day>={day15} and grade=5
    ) e on a.mbga_uid=e.mbga_uid and a.user_id=e.user_id and a.day=e.day and get_json_object(a.player,'$.player')=e.card_id
    left join (select *,'1' as a1 from g33002013.dim_rank) d on a.a1=d.a1
    left join
    (
        select session,count(distinct result) pvp
        from g33002013.match_snapshot where day>={day15}
        and ai='false'
        group by session
    ) b on a.session=b.session
    where a.star>=d.min_star and a.star<=d.max_star
    group by a.day,pvp,get_json_object(player,'$.player'),type,rank_name
) a
left join
(
    select type,count(distinct mbga_uid,session) total_match
    from g33002013.match_snapshot where day>={day15} and ai='false'
    group by type
) c on a.type=c.type
left join g33002013.dim_match d on a.type=d.id
left join g33002013.dim_card_h5 e on a.player=e.card_id
where pvp=2;

-- ==================================================================