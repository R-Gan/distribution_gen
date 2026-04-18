from src.calc_results._core import load_file, build_answers_map, build_votes_map, store_results_map, update_championship_values, calc_results_map, fetch_total_wins
from src.discord_formatter._core import load_username_override_map, generate_discord_results_markdown, generate_race_results_json

from pathlib import Path
from typing import Dict, List, Optional
import argparse
from datetime import date

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Calculate poll results into point allocations")
    parser.add_argument("--poll-file", required=True, help="Export poll from Discord as json and paste into a new file under /json_poll/")
    parser.add_argument("--hall-of-fame", default="hall_of_fame_records/weekly_results.json")
    parser.add_argument("--date", default=date.today().strftime("%Y-%m-%d"))
    parser.add_argument("--point-pool", type=int, default=100)
    parser.add_argument("--url", required=True, help="URL of the race results page on netkeiba, example: https://en.netkeiba.com/race/race_result.html?race_id=202609020611")
    parser.add_argument("--results_output-dir", default="live_results", help="Output directory for the generated results JSON file. Default is /live_results/")
    parser.add_argument("--results_output-file", required=True, help="Output file name for the generated results JSON file. Must end with .json. Default output directory is /live_results/")

    args = parser.parse_args(argv)

    print(args.date)
    
    generate_race_results_json(args.url, args.results_output_file, args.results_output_dir)
    race_results_path = Path(args.results_output_dir) / args.results_output_file

    points_map, first_place_answer_id = calc_results_map(args.poll_file, race_results_path, args.point_pool)

    username_override_map = load_username_override_map("username_override_map.json")

    # store the points map in the hall of fame records with the corresponding date
    store_results_map(points_map, args.hall_of_fame, args.date)
    
    # update the championship values in the hall of fame records based on the first place voters
    update_championship_values(args.poll_file, first_place_answer_id, args.hall_of_fame, args.date)
    
    # fetch the total number of wins for each player from the hall of fame records
    total_wins = fetch_total_wins(args.hall_of_fame)
    discord_markdown = generate_discord_results_markdown(args.hall_of_fame, total_wins, username_override_map, 3)

    print("\n==================================")
    print("BELOW IS DISCORD MARKDOWN TO COPY")
    print("==================================\n")

    print(discord_markdown)

if __name__ == "__main__":
    main()
