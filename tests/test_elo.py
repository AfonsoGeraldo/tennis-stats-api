from elo import update_ratings
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

def test_update_ratings():
    new_winner_rating_equal, new_loser_rating_equal = update_ratings(1500, 1500)
    new_winner_rating_fav, new_loser_rating_fav = update_ratings(1800, 1500)
    new_winner_rating_upset, new_loser_rating_upset = update_ratings(1500, 1800)

    assert new_winner_rating_equal + new_loser_rating_equal == pytest.approx(1500 + 1500, abs=0.01), "Ratings were not well calculated for equal initial ratings"
    assert new_winner_rating_fav + new_loser_rating_fav == pytest.approx(1800 + 1500, abs=0.01), "Ratings were not well calculated when favorite wins"
    assert new_winner_rating_upset + new_loser_rating_upset == pytest.approx(1500 + 1800, abs=0.01), "Ratings were not well calculated when there's an upset"