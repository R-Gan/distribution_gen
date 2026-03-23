from calc_results._core import build_votes_map, generate_points_map

dummy_results = [
    "Option A",
    "Option B",
    "Option C"
]
dummy_poll = {
        "answers": [
            {"id": "a1", "name": "Option A"},
            {"id": "a2", "name": "Option B"},
            {"id": "a3", "name": "Option C"},
        ],
        "votes": [
            {"answerId": "a1", "user": {"id": "u1", "username": "alice"}},
            {"answerId": "a1", "user": {"id": "u2", "username": "bob"}},
            {"answerId": "a2", "user": {"id": "u3", "username": "carol"}},
            {"answerId": "a3", "user": {"id": "u4", "username": "david"}},
        ],
    }

dummy_votes_map = build_votes_map(dummy_poll)


def test_build_votes_map_basic():

    expected = {
        "Option A": ["alice", "bob"],
        "Option B": ["carol"],
        "Option C": ["david"],
    }

    result = dummy_votes_map
    assert result == expected

def test_generate_points_map():
    scalars = [60, 30, 10]
    point_pool = 100

    # points_to_assign = (1 / (scalars[index] / count)) * point_pool
    expected_points_map = {
        "alice": (1 / (60.0 / 2)) * point_pool,  # Option A has 2 votes
        "bob": (1 / (60.0 / 2)) * point_pool,    # Option A has 2 votes
        "carol": (1 / (30.0 / 1)) * point_pool,   # Option B has 1 vote
        "david": (1 / (10.0 / 1)) * point_pool,   # Option C has 1 vote
    }

    result = generate_points_map(dummy_results, dummy_votes_map, scalars, point_pool)
    assert result == expected_points_map