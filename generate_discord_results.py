from src.calc_results._core import load_file, build_answers_map, build_votes_map, calc_results_map
from src.discord_formatter._core import load_username_override_map, generate_discord_markdown

from typing import Dict, List, Optional
import argparse

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Calculate poll results into point allocations")
    parser.add_argument("--poll-file", default="json_poll/poll_fab4d87b-747c-4127-bf26-419bb538147e.json")
    parser.add_argument("--results-file", default="live_results/results.json")
    parser.add_argument("--point-pool", type=int, default=100)

    args = parser.parse_args(argv)
    
    points_map = calc_results_map(args.poll_file, args.results_file, args.point_pool)

    username_override_map = load_username_override_map("username_override_map.json")
    discord_markdown = generate_discord_markdown(points_map, username_override_map)

    print("\n==================================")
    print("BELOW IS DISCORD MARKDOWN TO COPY")
    print("==================================\n")

    print(discord_markdown)

if __name__ == "__main__":
    main()
