-- 9. Match Participation by Rank (weeklyreport_matchrank)
-- ==================================================================
-- Description: Match stats broken down by player's rank.
select a.day,c.name type,rank_name,count(distinct a.mbga_uid,a.user_id) uu,count(distinct a.mbga_uid,a.session) matchs,sum(match_time) match_time,
count(distinct case when a.result='true' then concat(a.mbga_uid,a.session) else null end) win,
count(distinct case when a.result<>b.result and b.players<>0 then concat(a.mbga_uid,a.session) else null end) pvp_times,
count(distinct case when a.result='true' and a.result<>b.result and b.players<>0 then concat(a.mbga_uid,a.session) else null end) pvp_win
from
(
    SELECT day,mbga_uid,user_id,session,type,match_time,split(star,'#')[0] star,result,'1' as a1
    from g33002013.daily_match_snapshot
    where day>={day15} and ai='false'
) a
left join (select *,'1' as a1 from g33002013.dim_rank) d on a.a1=d.a1
left join g33002013.dim_match c on a.type=c.id
left join
(
    SELECT session,result,count(DISTINCT case when ai='false' then user_id else null end) players
    from g33002013.daily_match_snapshot
    where day>={day15}
    group by session,result
) b on a.session=b.session
left join g33002013.user_blacklist e on a.mbga_uid=e.mbga_uid
where a.star>=d.min_star and a.star<=d.max_star and e.mbga_uid is null
group by a.day,c.name,rank_name;

-- ==================================================================