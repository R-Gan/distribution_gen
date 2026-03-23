from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from src.distribution_gen._core import generate_distribution


def load_file(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        # try relative to this file
        p = Path(__file__).parent.joinpath(path)
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def build_answers_map(poll: dict) -> Dict[str, str]:
    """Return a mapping of answer `id` -> `name`."""
    answers = poll.get("answers", [])
    return {a["id"]: a.get("name", "") for a in answers}


def build_votes_map(poll: dict) -> Dict[str, List[str]]:
    """Return a mapping of answer `name` -> list of usernames.

    This function is pure and safe to import; it does not perform I/O.
    """
    votes = poll.get("votes", [])
    answers_map = build_answers_map(poll)  # answerId -> name
    out: Dict[str, List[str]] = defaultdict(list)
    for v in votes:
        answer_id = v.get("answerId")
        # map answer id to its display name
        answer_name = answers_map.get(answer_id)
        if not answer_name:
            continue
        user = v.get("user") or {}
        username = user.get("username")
        if username:
            out[answer_name].append(username)
    return dict(out)


def generate_points_map(results: List[str], votes_map: Dict[str, List[str]], scalars: List[float], point_pool: int) -> Dict[str, float]:
    """Given the ordered results and votes map, compute the points map."""
    points_map: Dict[str, float] = {}
    for index, result in enumerate(results):
        # get the number of users that selected this answer
        count = len(votes_map.get(result, []))
        if count == 0:
            continue

        # (prize pool * (scalar/100)) / n people that picked that answer

        points_to_assign = (point_pool * (scalars[index] / 100)) / count
        # points_to_assign = (1 / (scalars[index] / count)) * point_pool
        # loop through users that voted for this answer and assign points
        for user in votes_map.get(result, []):
            points_map[user] = points_map.get(user, 0.0) + points_to_assign
    return points_map

def calc_results_map(poll_file: str, results_file: str, point_pool: int = 100) -> Dict[str, float]:
    """Run the scoring using explicit file paths and return a points map.

    This can be called programmatically without triggering CLI parsing.
    """
    poll = load_file(poll_file)
    results = load_file(results_file).get("results", [])

    # key: answer name, value: list of usernames
    votes_map = build_votes_map(poll)
    # print(f"Votes map (answer name -> list of usernames):\n{json.dumps(votes_map, indent=2)}")

    _, scalars = generate_distribution()
    # print(f"Scalars: {scalars}")

    points_map = generate_points_map(results, votes_map, scalars, point_pool)

    # return the computed points map for programmatic consumption
    return points_map


# pulls from optional command line args
def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Calculate poll results into point allocations")
    parser.add_argument("--poll-file", default="src/json_poll/test_poll.json")
    parser.add_argument("--results-file", default="src/live_results/results.json")
    parser.add_argument("--point-pool", type=int, default=100)
    args = parser.parse_args(argv)

    points_map = calc_results_map(args.poll_file, args.results_file, args.point_pool)

    print("\nPoints map (username -> points):")
    for k, v in points_map.items():
        print(f"- {k}: {v:.2f}")


if __name__ == "__main__":
    main()
