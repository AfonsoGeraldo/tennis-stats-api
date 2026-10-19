from db_utils import get_engine
from ingestion import read_players, read_matches, build_players, build_tournaments, build_matches, clear_tables, load_table

def run_ingestion(years):

    try:
        # 1. read data
        print("Reading data...")
        df_players = read_players()
        df_matches = read_matches(years)
        
        # 2. build data
        print("Building data...")
        players = build_players(df_players)
        tournaments = build_tournaments(df_matches)
        matches = build_matches(df_matches)

        if players is None or tournaments is None or matches is None:
            print("There was an error while building tables. Please check it.")
            return False

        # 3. clear_tables
        print("Clearing tables...")
        engine = get_engine()
        clean = clear_tables(engine)

        if not clean:
            print("The tables are not clean. Please check it.")
            return False

        # 4. load tables
        print("Loading tables...")
        
        load_players = load_table(players, "Player", engine)
        if not load_players:
            print("There was an error while loading players.")
            return False
        
        load_tournaments = load_table(tournaments, "Tournament", engine)
        if not load_tournaments:
            print("There was an error while loading tournaments.")
            return False
        
        load_matches = load_table(matches, "TennisMatch", engine)
        if not load_matches:
            print("There was an error while loading matches.")
            return False
        
        print("Success!")
        return True

    except Exception as e:
        print("The following error occured while running ingestion: ", e)
        return False

if __name__ == "__main__":
    run_ingestion([2023, 2024, 2025])