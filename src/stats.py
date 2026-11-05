import pandas as pd
from db_utils import get_engine
from sqlalchemy import text

def get_surface_win_rates(player_id, engine):
    try:
        query = text("""select
                        t.surface,
                        count(*) as matches_played,
                        SUM(CASE
                                WHEN tm.winner_id = :player_id THEN 1
                                ELSE 0
                            END) as wins,
                        CAST(SUM(CASE WHEN tm.winner_id = :player_id THEN 1 ELSE 0 END)as decimal)/COUNT(*) as win_rate
                    from tennisMatch tm
                    inner join tournament t
                    on
                        tm.tourney_id = t.tourney_id
                    where
                        (tm.winner_id = :player_id or tm.loser_id = :player_id)
                        and tm.is_wo = 0
                    group by
                        t.surface""")
        df = pd.read_sql(query, engine, params={"player_id": player_id})
        return df   
    except Exception as e:
        print("There was an error while loading surface win rates: ", e)
        return None

def get_head_to_head(player1_id, player2_id, engine):
    try:
        query = text("""
                    select
                        t.tourney_date, t.tourney_name, t.surface, tm.round, tm.winner_id, tm.score
                    from TennisMatch tm
                    inner join Tournament t
                    on
                        tm.tourney_id = t.tourney_id
                    where
                        tm.is_wo = 0
                        and ((tm.winner_id = :player1_id and tm.loser_id = :player2_id) or (tm.winner_id = :player2_id and tm.loser_id = :player1_id))
                    ORDER BY t.tourney_date DESC
                    """)
        df = pd.read_sql(query, engine, params={"player1_id": player1_id, "player2_id": player2_id})
        return df
    except Exception as e:
        print("There was an error while loading h2h: ", e)
        return None

def get_head_to_head_summary(matches, player1_id, player2_id):
    try:
        if matches is None: 
            print("There are no matches to check the h2h.")
            return None
        
        counts = matches['winner_id'].value_counts()
        player1_count = counts.get(player1_id, 0)
        player2_count = counts.get(player2_id, 0)

        h2h = {
            "player1_wins": int(player1_count),
            "player2_wins": int(player2_count),
            "total" : int(player1_count + player2_count)
        }

        return h2h
    except Exception as e:
        print("There was an error while counting h2h: ", e)
        return None


def get_recent_form(player_id, last, engine):
    try:
        query = text("""
                    select
                        top (:last) 
                        t.tourney_date, 
                        t.tourney_name, 
                        t.surface, 
                        tm.[round],
                        case
                            when tm.winner_id = :player_id then	tm.loser_id
                            else tm.winner_id
                        end as opponent_id,
                        case
                            when tm.winner_id = :player_id then	'W'
                            else 'L'
                        end as result,
                        tm.score
                    from TennisMatch tm
                    inner join Tournament t
                    on
                        tm.tourney_id = t.tourney_id
                    where
                        (tm.winner_id = :player_id 
                        or tm.loser_id = :player_id)
                        and tm.is_wo = 0
                    order by
                        t.tourney_date desc,
                        tm.match_num desc
                """)
        df = pd.read_sql(query, engine, params={"player_id": player_id, "last": last})
        return df
    except Exception as e:
        print("There was an error while loading recent form: ", e)
        return None


def get_elo_ranking(rating_type, limit, engine):
    try:
        query = text(
            """
            ;WITH latest AS (
            SELECT
                er.player_id,
                er.rating,
                t.tourney_date AS last_match_date,
                ROW_NUMBER() OVER (
                    PARTITION BY er.player_id
                    ORDER BY t.tourney_date DESC, tm.match_num DESC
                ) AS rn
            FROM EloRating er
            INNER JOIN TennisMatch tm ON tm.match_id = er.match_id
            INNER JOIN Tournament t   ON t.tourney_id = tm.tourney_id
            WHERE er.rating_type = :rating_type
        )
        SELECT TOP (:limit)
            p.player_id,
            p.name_first,
            p.name_last,
            l.rating,
            l.last_match_date
        FROM latest l
        INNER JOIN Player p ON p.player_id = l.player_id
        WHERE l.rn = 1
        ORDER BY l.rating DESC;
            """
        )
        df = pd.read_sql(query, engine, params={"limit": limit, "rating_type": rating_type})
        return df
    except Exception as e:
            print("There was an error while loading elo ranking: ", e)
            return None 


if __name__ == "__main__":
    engine = get_engine()
    matches = get_head_to_head(207989, 206173, engine)
    # print(get_surface_win_rates(999999999, engine))
    # print(get_head_to_head(207989, 206173, engine))
    # print(get_head_to_head_summary(matches, 207989, 206173))
    # print(get_recent_form(207989, 10, engine))
    print(get_elo_ranking('Overall', 10, engine))
    print("CLAY \n")
    print(get_elo_ranking('Clay', 10, engine))
    print("GRASS \n")
    print(get_elo_ranking('Grass', 10, engine))
    print("HARD \n")
    print(get_elo_ranking('Hard', 10, engine))
    #207989