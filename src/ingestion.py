import pandas as pd
from sqlalchemy import text
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent   # src/ingestion.py → src/ → project root
DATA_DIR = PROJECT_ROOT / "data"

logger = logging.getLogger(__name__)

# Extract functions - read_players e read_matches
def read_players():
    try:
        df_players = pd.read_csv(DATA_DIR / "atp_players.csv", dtype={'wikidata_id': str})
        logger.info("Read %d players", len(df_players))
        return df_players
    except Exception as e:
        logger.exception("Error while extracting players data.")
        return None

def read_matches(years):
    try:
        dfs = []
        for year in years:
            df = pd.read_csv(DATA_DIR / f"atp_matches_{year}.csv")
            dfs.append(df)

        df_all = pd.concat(dfs).reset_index(drop=True)
        logger.info("Read %d matches", len(df_all))
        return df_all

    except Exception as e:
        logger.exception("Error while extracting matches data.")
        return None

#Transform functions

def convert_date(series):
    try:
        date_converted = pd.to_datetime(series, errors='coerce', format='%Y%m%d')
        lost = series.notna().sum() - date_converted.notna().sum()
        if lost > 0:
            logger.warning("%d values in '%s' could not be parsed as dates", lost, series.name)

        return date_converted
    except Exception as e:
        logger.exception("Error while converting dates.")
        return None
    

def build_tournaments(matches_raw):
    try:
        tourneys = matches_raw[['tourney_id', 'tourney_name', 'tourney_date', 'tourney_level', 'surface']].drop_duplicates().copy()
        tourneys['tourney_date'] = convert_date(tourneys['tourney_date'])
        logger.info("Built %d tournaments.", len(tourneys))
        return tourneys
    except Exception as e:
        logger.exception("Error while building tournaments.")
        return None

def build_players(players_raw):
    try:
        players = players_raw.loc[players_raw['name_last'].notna(), ['player_id', 'name_first','name_last','hand', 'dob', 'ioc', 'height']].copy()
        players['dob'] = convert_date(players['dob'])
        logger.info("Built %d players.", len(players))
        return players
    except Exception as e:
        logger.exception("Error while building players.")
        return None

def build_matches(matches_raw):
    try:
        matches = matches_raw[['tourney_id', 'match_num', 'round', 'winner_id', 'loser_id', 'winner_rank', 'loser_rank', 'score']].copy()
        matches['is_wo'] = matches['score'].str.contains('W/O', na=False)
        matches['is_retirement'] = matches['score'].str.contains('RET', na=False)
        logger.info("Built %d matches.", len(matches))
        return matches
    except Exception as e:
        logger.exception("Error while building matches.")
        return None

def load_table(df, table_name, engine):
    if df is not None:
        try:
            df.to_sql(table_name, engine, if_exists='append', index=False)
            logger.info("Loaded %d rows into %s", len(df), table_name)
            return True
        except Exception as e:
            logger.exception("There's an error while loading table %s.", table_name)
            return False
    else:
        logger.error("No data to load into %s", table_name)
        return False

def clear_tables(engine):
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM EloRating"))
            conn.execute(text("DBCC CHECKIDENT ('EloRating', RESEED, 0)"))
            conn.execute(text("DELETE FROM TennisMatch"))
            conn.execute(text("DBCC CHECKIDENT ('TennisMatch', RESEED, 0)"))
            conn.execute(text("DELETE FROM Player"))
            conn.execute(text("DELETE FROM Tournament"))
        logger.info("Tables cleared.")
        return True
    except Exception as e:
        logger.exception("Error while clearing tables.")
        return False