from src.calc_results._core import load_file, build_answers_map, build_votes_map, store_results_map, update_championship_values, calc_results_map
from src.discord_formatter._core import load_username_override_map, generate_discord_results_markdown, generate_discord_results_markdown_two

from typing import Dict, List, Optional
import argparse
from datetime import date

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Calculate poll results into point allocations")
    parser.add_argument("--poll-file", default="json_poll/test_poll.json")
    parser.add_argument("--race-results", default="live_results/results.json")
    parser.add_argument("--hall-of-fame", default="hall_of_fame_records/weekly_results.json")
    parser.add_argument("--date", default=date.today().strftime("%Y-%m-%d"))
    parser.add_argument("--point-pool", type=int, default=100)

    args = parser.parse_args(argv)

    print(args.date)
    
    points_map, first_place_answer_id = calc_results_map(args.poll_file, args.race_results, args.point_pool)


    username_override_map = load_username_override_map("username_override_map.json")
    # store the points map in the hall of fame records with the corresponding date
    store_results_map(points_map, args.hall_of_fame, args.date)
    # update the championship values in the hall of fame records based on the first place voters
    update_championship_values(args.poll_file, first_place_answer_id, args.hall_of_fame, args.date)
    discord_markdown = generate_discord_results_markdown_two(args.hall_of_fame, username_override_map, 3)

    print("\n==================================")
    print("BELOW IS DISCORD MARKDOWN TO COPY")
    print("==================================\n")

    print(discord_markdown)

if __name__ == "__main__":
    main()
