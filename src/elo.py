import pandas as pd

def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_ratings(winner_rating, loser_rating, k=32):

    if winner_rating is None or loser_rating is None:
        raise ValueError("Ratings can't be none.")
    
    expected = expected_score(winner_rating, loser_rating)
    change = 1-expected

    new_winner_rating = winner_rating + k * change
    new_loser_rating = loser_rating + k * (-change)

    return new_winner_rating, new_loser_rating

def compute_elo(matches):

    ordered_matches = matches.sort_values(by=['tourney_date', 'match_num'])
    
    rows = []
    overall_ratings = {}
    surface_ratings = {'Hard': {}, 'Clay': {}, 'Grass': {}}

    for match in ordered_matches.itertuples():

        winner_current = overall_ratings.get(match.winner_id, 1500)
        loser_current = overall_ratings.get(match.loser_id, 1500)
        new_winner_rating, new_loser_rating = update_ratings(winner_current, loser_current)

        overall_ratings[match.winner_id] = new_winner_rating
        overall_ratings[match.loser_id] = new_loser_rating

        rows.append({'player_id': match.winner_id, 'match_id': match.match_id, 'rating_type': 'Overall', 'rating': new_winner_rating})
        rows.append({'player_id': match.loser_id, 'match_id': match.match_id, 'rating_type': 'Overall', 'rating': new_loser_rating})

        if pd.notna(match.surface):

            ratings = surface_ratings[match.surface]

            surface_winner_current = ratings.get(match.winner_id, 1500)
            surface_loser_current = ratings.get(match.loser_id, 1500)
            new_surface_winner_rating, new_surface_loser_rating = update_ratings(surface_winner_current, surface_loser_current)
    
            ratings[match.winner_id] = new_surface_winner_rating
            ratings[match.loser_id] = new_surface_loser_rating
    
            rows.append({'player_id': match.winner_id, 'match_id': match.match_id, 'rating_type': match.surface, 'rating': new_surface_winner_rating})
            rows.append({'player_id': match.loser_id, 'match_id': match.match_id, 'rating_type': match.surface, 'rating': new_surface_loser_rating})

    return pd.DataFrame(rows)

