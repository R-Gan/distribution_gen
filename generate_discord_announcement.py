from src.calc_results._core import load_file, build_answers_map, build_votes_map, calc_results_map
from src.discord_formatter._core import generate_discord_announcement_markdown, load_race_lineups_map

from typing import Dict, List, Optional
import argparse

def main(argv: Optional[List[str]] = None) -> None:
    TOTAL_HORSE = 18
    parser = argparse.ArgumentParser(description="Calculate poll results into point allocations")
    parser.add_argument("--poll-file", default="json_poll/test_poll.json")
    parser.add_argument("--results-file", default="live_results/results.json")
    parser.add_argument("--point-pool", type=int, default=100)

    args = parser.parse_args(argv)
    
    points_map = calc_results_map(args.poll_file, args.results_file, args.point_pool)

    race_lineups = load_race_lineups_map("race_lineups")
    discord_markdown = generate_discord_announcement_markdown(race_lineups, TOTAL_HORSE)

    print("\n==================================")
    print("BELOW IS DISCORD MARKDOWN TO COPY")
    print("==================================\n")

    print(discord_markdown)

if __name__ == "__main__":
    main()
