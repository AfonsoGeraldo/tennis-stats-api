import pandas as pd

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
