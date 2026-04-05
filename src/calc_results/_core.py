from __future__ import annotations

import argparse
import json
from collections import defaultdict
from os import path
from pathlib import Path
from typing import Any, Dict, List, Optional

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

    # get the 1st place answerid
    first_place_horse = results[0] if len(results) > 0 else None
    first_place_answer_id = ""
    # print(f"First place horse: {first_place_horse}")
    answers = poll.get("answers", [])
    for answer in answers:
        if answer.get("name") == first_place_horse:
            first_place_answer_id = answer.get("id")
            # print(f"First place horse answer ID: {first_place_answer_id}")
            break

    # key: answer name, value: list of usernames
    votes_map = build_votes_map(poll)
    # print("Votes map (answer name -> list of usernames):")
    # for answer, users in votes_map.items():
    #     print(f"  {answer}: {users}")

    _, scalars = generate_distribution()
    # print(f"Scalars: {scalars}")

    points_map = generate_points_map(results, votes_map, scalars, point_pool)

    # return the computed points map for programmatic consumption
    return points_map, first_place_answer_id


def build_weekly_results_players(
    points_map: Dict[str, float],
) -> Dict[str, dict]:
    """Build the player records for a weekly results entry."""
    players: Dict[str, dict] = {}
    for username, points in sorted(points_map.items()):
        players[username] = {
            "points": round(points, 2),
            "first_place": False,
        }
    return players


def build_weekly_results_entry(
    date: str,
    points_map: Dict[str, float],
) -> Dict[str, Any]:
    return {
        "date": date,
        "players": build_weekly_results_players(points_map),
    }


def append_weekly_results(path: str, entry: Dict[str, Any]) -> None:
    p = Path(path)
    if not p.exists():
        p = Path(__file__).parent.joinpath(path)

    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)

    content = {"results": []}
    if p.exists():
        with p.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
            if isinstance(raw, dict):
                content = raw

    if not isinstance(content.get("results"), list):
        content["results"] = []

    content["results"].append(entry)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(content, fh, indent=4, ensure_ascii=False)

# append a results record with calced points_map, the first_place field will currently be a placeholder for a 2nd passthrough to fill
def store_results_map(
    points_map: Dict[str, float],
    path: str,
    date: str,
) -> None:
    print(f"Storing points map to {path}...")
    entry = build_weekly_results_entry(date, points_map)
    append_weekly_results(path, entry)


def update_championship_values(
    poll_file: str,
    first_place_answer_id: str,
    hall_of_fame_path: str,
    date: str,
) -> None:
    with open(hall_of_fame_path, "r") as f:
        hall_of_fame_data = json.load(f)

    poll = load_file(poll_file)
    votes = poll.get("votes", [])

    # get list of all users that voted for the first place answer
    first_place_voters = [vote.get("user", {}).get("username") for vote in votes if vote.get("answerId") == first_place_answer_id]
    print(f"Users that voted for the first place answer (answer ID {first_place_answer_id}): {first_place_voters}")

    date_index = 0
    for record in hall_of_fame_data.get("results", []):
        if record.get("date") == date:
            print(f"Found matching date {date} in hall of fame records, date_index set...")
            break
        date_index += 1

    for voter in first_place_voters:
        hall_of_fame_data["results"][date_index]["players"][voter]["first_place"] = True

    # save back the players json to the hall of fame records
    with open(hall_of_fame_path, "w") as f:
        json.dump(hall_of_fame_data, f, indent=4)

    print(f"Updated championship values in {hall_of_fame_path}...")

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
