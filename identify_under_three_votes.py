from src.calc_results._core import load_file, build_answers_map, build_votes_map, calc_results_map
from src.discord_formatter._core import load_username_override_map

from typing import Dict, List, Optional
import argparse

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Calculate poll results into point allocations")
    parser.add_argument("--poll-file", default="json_poll/test_poll.json")

    args = parser.parse_args(argv)
    
    vote_count_map: Dict[str, int] = {}

    poll = load_file(args.poll_file)

    # tabulate the number of votes by each user
    for v in poll.get("votes", []):
        user = v.get("user") or {}
        username = user.get("username")
        if username:
            vote_count_map[username] = vote_count_map.get(username, 0) + 1

    override_map = load_username_override_map("username_override_map.json")

    # identify users with under three votes
    under_three_votes = [username for username, count in vote_count_map.items() if count < 3]
    
    print(f"Users with under three votes:\n\n")
    for username in under_three_votes:
        print(f"User {override_map.get(username, username)} ({username}) has {vote_count_map[username]} votes")
    print ("\n\n")    

    # print(f"\n\nUsers with under three votes: {', '.join(global_names)}\n\n")

if __name__ == "__main__":
    main()
