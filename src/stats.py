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
    except Excpetion as e:
        print("There was an error while loading h2h: ", e)
        return None


if __name__ == "__main__":
    engine = get_engine()
    print(get_surface_win_rates(999999999, engine))
    print(get_head_to_head(207989, 206173, engine))
    #207989