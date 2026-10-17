import pandas as pd
import sys
sys.path.append('../src')
from db_utils import get_engine

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
        players = players_raw[['player_id', 'name_first','name_last','hand', 'dob', 'ioc', 'height']].copy()
        players['dob'] = convert_date(players['dob'])
        return players
    except Exception as e:
        print("There's an error while building players : ", e)
        return None

# def build_matches(matches_raw):