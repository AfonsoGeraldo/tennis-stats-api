import pandas as pd
import sys
sys.path.append('../src')
from db_utils import get_engine
from sqlalchemy import text

# Extract functions - read_players e read_matches
def read_players():
    try:
        df_players = pd.read_csv('data/atp_players.csv', dtype={'wikidata_id': str})
        return df_players
    except Exception as e:
        print("There's an error while extracting players data: ", e)
        return None

def read_matches(years):
    try:
        dfs = []
        for year in years:
            df = pd.read_csv(f'data/atp_matches_{year}.csv')
            dfs.append(df)

        df_all = pd.concat(dfs).reset_index(drop=True)
        return df_all

    except Exception as e:
        print("There's an error while extracting matches data: ", e)
        return None

#Transform functions

def convert_date(series):
    try:
        date_converted = pd.to_datetime(series, errors='coerce', format='%Y%m%d')
        return date_converted
    except Exception as e:
        print("There's an error while converting dates : ", e)
        return None
    

def build_tournaments(matches_raw):
    try:
        tourneys = matches_raw[['tourney_id', 'tourney_name', 'tourney_date', 'tourney_level', 'surface']].drop_duplicates().copy()
        tourneys['tourney_date'] = convert_date(tourneys['tourney_date'])
        return tourneys
    except Exception as e:
        print("There's an error while building tournaments : ", e)
        return None

def build_players(players_raw):
    try:
        players = players_raw.loc[players_raw['name_last'].notna(), ['player_id', 'name_first','name_last','hand', 'dob', 'ioc', 'height']].copy()
        players['dob'] = convert_date(players['dob'])
        return players
    except Exception as e:
        print("There's an error while building players : ", e)
        return None

def build_matches(matches_raw):
    try:
        matches = matches_raw[['tourney_id', 'match_num', 'round', 'winner_id', 'loser_id', 'winner_rank', 'loser_rank', 'score']].copy()
        matches['is_wo'] = matches['score'].str.contains('W/O', na=False)
        matches['is_retirement'] = matches['score'].str.contains('RET', na=False)
        return matches
    except Exception as e:
        print("There's an error while building matches : ", e)
        return None

def load_table(df, table_name, engine):
    if df is not None:
        try:
            df.to_sql(table_name, engine, if_exists='append', index=False)
            return True
        except Exception as e:
            print(f"There's an error while loading table {table_name}: {e}")
            return False
    else:
        print(f"No data to load into {table_name}")
        return False

def clear_tables(engine):
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM TennisMatch"))
            conn.execute(text("DBCC CHECKIDENT ('TennisMatch', RESEED, 0)"))
            conn.execute(text("DELETE FROM Player"))
            conn.execute(text("DELETE FROM Tournament"))
        return True
    except Exception as e:
        print(f"There's an error while clearing tables: {e}")
        return False