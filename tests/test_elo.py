from elo import update_ratings, compute_elo
from stats import get_head_to_head_summary
import pandas as pd
import pytest

def test_update_ratings_equal_players():
    new_winner_rating, new_loser_rating = update_ratings(1500, 1500)
    assert new_winner_rating == pytest.approx(1516.00, abs=0.01), "New winner rating were not updated as expected"
    assert new_loser_rating == pytest.approx(1484.00, abs=0.01), "New loser rating were not updated as expected"

def test_update_ratings_favorite_wins():
    new_winner_rating, new_loser_rating = update_ratings(1800, 1500)
    assert new_winner_rating == pytest.approx(1804.83, abs=0.01), "New winner rating were not updated as expected"
    assert new_loser_rating == pytest.approx(1495.17, abs=0.01), "New loser rating were not updated as expected"
    
def test_update_ratings_upset():
    new_winner_rating, new_loser_rating = update_ratings(1500, 1800)
    assert new_winner_rating == pytest.approx(1527.17, abs=0.01), "New winner rating were not updated as expected"
    assert new_loser_rating == pytest.approx(1772.83, abs=0.01), "New loser rating were not updated as expected"

def test_update_ratings_none_raises():
    with pytest.raises(ValueError):
        update_ratings(None, 1500)

def test_update_ratings_preserves_total():
    new_winner_rating_equal, new_loser_rating_equal = update_ratings(1500, 1500)
    new_winner_rating_fav, new_loser_rating_fav = update_ratings(1800, 1500)
    new_winner_rating_upset, new_loser_rating_upset = update_ratings(1500, 1800)

    assert new_winner_rating_equal + new_loser_rating_equal == pytest.approx(1500 + 1500, abs=0.01), "Ratings were not well calculated for equal initial ratings"
    assert new_winner_rating_fav + new_loser_rating_fav == pytest.approx(1800 + 1500, abs=0.01), "Ratings were not well calculated when favorite wins"
    assert new_winner_rating_upset + new_loser_rating_upset == pytest.approx(1500 + 1800, abs=0.01), "Ratings were not well calculated when there's an upset"

def test_compute_elo_rating_carries_between_matches():
    matches = pd.DataFrame({
        'match_id':     [1, 2],
        'tourney_date': ['2024-01-01', '2024-01-01'],
        'match_num':    [1, 2],
        'winner_id':    [10, 10],
        'loser_id':     [20, 30],
        'surface':      ['Hard', 'Hard'],
    })

    ratings = compute_elo(matches)
    player10_ratings = ratings[(ratings['player_id'] == 10)  & (ratings['match_id'] == 2) & (ratings['rating_type'] == 'Overall')]
    assert player10_ratings['rating'].iloc[0] == pytest.approx(1531.26, abs=0.01), "Ratings were not well calculated."

def test_compute_elo_shuffled_input():
    matches = pd.DataFrame({
    'match_id':     [2, 1],
    'tourney_date': ['2024-01-01', '2024-01-01'],
    'match_num':    [2, 1],
    'winner_id':    [10, 10],
    'loser_id':     [30, 20],
    'surface':      ['Hard', 'Hard'],
})
    ratings = compute_elo(matches)
    player10_ratings_overall = ratings[(ratings['player_id'] == 10)  & (ratings['match_id'] == 2) & (ratings['rating_type'] == 'Overall')]    
    assert player10_ratings_overall['rating'].iloc[0] == pytest.approx(1531.26, abs=0.01), "Rating changed when input order changed."

def test_compute_elo_surfaces_are_independent():
    matches = pd.DataFrame({
        'match_id':     [1, 2],
        'tourney_date': ['2024-01-01', '2024-01-01'],
        'match_num':    [1, 2],
        'winner_id':    [10, 10],
        'loser_id':     [20, 30],
        'surface':      ['Hard', 'Clay'],
    })

    ratings = compute_elo(matches)
    player10_ratings_overall = ratings[(ratings['player_id'] == 10)  & (ratings['match_id'] == 2) & (ratings['rating_type'] == 'Overall')]
    player10_ratings_clay = ratings[(ratings['player_id'] == 10)  & (ratings['match_id'] == 2) & (ratings['rating_type'] == 'Clay')]
    assert player10_ratings_overall['rating'].iloc[0] == pytest.approx(1531.26, abs=0.01), "Overall ratings were not well calculated."
    assert player10_ratings_clay['rating'].iloc[0] == pytest.approx(1516.00, abs=0.01), "Clay ratings were not well calculated."

def test_head_to_head_summary_counts_wins():
    matches = pd.DataFrame({'winner_id': [10, 20, 10]})

    summary = get_head_to_head_summary(matches, 10, 20)

    assert summary == {
        "player1_id": 10,
        "player1_wins": 2,
        "player2_id": 20,
        "player2_wins": 1,
        "total": 3,
    }


def test_head_to_head_summary_player_never_won():
    matches = pd.DataFrame({'winner_id': [10, 10, 10]})

    summary = get_head_to_head_summary(matches, 10, 20)

    assert summary == {
        "player1_id": 10,
        "player1_wins": 3,
        "player2_id": 20,
        "player2_wins": 0,
        "total": 3,
    }


def test_head_to_head_summary_none_input():
    assert get_head_to_head_summary(None, 10, 20) is None
