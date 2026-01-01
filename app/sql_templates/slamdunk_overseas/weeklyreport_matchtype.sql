-- 7. Match Participation (weeklyreport_matchtype)
-- ==================================================================
-- Description: Match stats (Times, Win, PvP vs AI) by match type.
select all_uu,b.type,match_times,uu,times,win,pvp_uu,pvp_times,pvp_win,ping,a.day
from
(
    select day,count(distinct user_id,mbga_uid) all_uu
    from g33002013.daily_game_log
    where day >={day15}
    group by day
) a
left join
(
    select a.day,c.name type,count(distinct a.match_id) as match_times,
    count(distinct a.mbga_uid) uu,count(distinct a.mbga_uid,log_t) times,
    count(distinct case when reuslt='true' then concat(a.mbga_uid,log_t) else null end) win,
    count(distinct case when AI_num<TAR_num then a.match_id else null end) as match_pvp_times,
    count(distinct case when AI_num<TAR_num then a.mbga_uid else null end) as pvp_uu,
    count(distinct case when AI_num<TAR_num then concat(a.mbga_uid,log_t) else null end) as pvp_times,
    count(distinct case when AI_num<TAR_num and reuslt='true' then concat(a.mbga_uid,log_t) else null end) pvp_win
    from
    (
        select day,get_json_object(a_tar,'$.type') as type,get_json_object(a_tar,'$.match_id') as match_id,mbga_uid,user_id,log_t,get_json_object(a_tar,'$.reuslt') reuslt
        from g33002013.daily_game_log
        where day >={day15}
        and a_typ in ('match_fight','arena_fight','com_fight','custom_fight')
        union all
        select day,'tower_fight' as type,concat(log_t,mbga_uid) as match_id,mbga_uid,user_id,log_t,get_json_object(a_tar,'$.reuslt') reuslt
        from g33002013.daily_game_log
        where day >={day15}
        and a_typ ='tower_fight'
    ) a 
    left join
    (
        select match_id,count(distinct case when substr(teammate,1,2)='23' then teammate else null end) AI_num,count(distinct teammate) TAR_num
        from
        (
            select distinct day,match_id,regexp_replace(teammate_id2,'\\[|\\]|"','') as teammate
            from
            (
                select distinct day,get_json_object(a_tar,'$.match_id') match_id,get_json_object(a_tar,'$.target_id') teammate_id
                from g33002013.daily_game_log
                where day >={day15}
                and a_typ in ('match_fight','arena_fight','com_fight','custom_fight')
            ) a
            LATERAL VIEW explode(split(teammate_id,',')) teammate as teammate_id2
        ) a
        group by match_id
    ) b on a.match_id=b.match_id
    left join g33002013.dim_match c on a.type=c.id
    group by a.day,c.name
) b on a.day=b.day
left join
(
    select a.day,name as type,ping
    from
    (
        select day,get_json_object(a_tar,'$.type') type,sum(get_json_object(a_tar,'$.ping')) ping
        from g33002013.daily_game_log
        where day>={day15}
        and a_typ='fight_data'
        group by day,get_json_object(a_tar,'$.type')
    ) a left join g33002013.dim_match b on a.type=b.id
) c on b.day=c.day and b.type=c.type
where b.type is not null;

-- ==================================================================