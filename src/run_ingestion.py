from db_utils import get_engine
from ingestion import read_players, read_matches, build_players, build_tournaments, build_matches, clear_tables, load_table
from elo import compute_elo, read_elo_matches
import logging
import os

logger = logging.getLogger(__name__)

def run_ingestion(years):

    try:
        # 1. read data
        logger.info("Reading data...")
        df_players = read_players()
        df_matches = read_matches(years)

        if df_players is None:
            logger.error("Players were not imported. Please check the CSV players file.")
            return False
        
        if df_matches is None:
            logger.error("Matches were not imported. Please check the CSV matches file.")
            return False        
        
        # 2. build data
        logger.info("Building data...")
        players = build_players(df_players)
        tournaments = build_tournaments(df_matches)
        matches = build_matches(df_matches)

        if players is None or tournaments is None or matches is None:
            logger.error("There was an error while building tables. Please check it.")
            return False

        # 3. clear_tables
        logger.info("Clearing tables...")
        engine = get_engine()
        clean = clear_tables(engine)

        if not clean:
            logger.error("The tables are not clean. Please check it.")
            return False

        # 4. load tables
        logger.info("Loading tables...")
        
        load_players = load_table(players, "Player", engine)
        if not load_players:
            logger.error("There was an error while loading players.")
            return False
        
        load_tournaments = load_table(tournaments, "Tournament", engine)
        if not load_tournaments:
            logger.error("There was an error while loading tournaments.")
            return False
        
        load_matches = load_table(matches, "TennisMatch", engine)
        if not load_matches:
            logger.error("There was an error while loading matches.")
            return False

        # 5. Calculate eloRatings
        logger.info("Computing Elo ratings...")
        elo_matches = read_elo_matches(engine)
        if elo_matches is None:
            logger.error("There was an error while reading matches for Elo.")
            return False

        elo_ratings = compute_elo(elo_matches)

        load_elo_ratings = load_table(elo_ratings, "EloRating", engine)
        if not load_elo_ratings:
            logger.error("There was an error while loading elo ratings.")
            return False
        
        logger.info("Success!")
        return True

    except Exception as e:
        logger.exception("Error while running ingestion.")
        return False

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/ingestion.log"),   # write to a file
            logging.StreamHandler(),                     # and show in the terminal
        ],
    )
    run_ingestion([2023, 2024, 2025])