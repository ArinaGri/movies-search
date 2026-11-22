from utils.ranking import weighted_rating

def test_weighted_rating_between_mean_and_movie_rating():
    row = {"vote_count": 100, "vote_average": 9.0}
    assert weighted_rating(row, global_mean=7.0, min_votes=100) == 8.0

def test_weighted_rating_with_no_votes():
    row = {"vote_count": 0, "vote_average": 0.0}
    assert weighted_rating(row, global_mean=7.0, min_votes=0) == 0
