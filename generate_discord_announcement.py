from pathlib import Path
from src.calc_results._core import load_file, build_answers_map, build_votes_map, calc_results_map
from src.discord_formatter._core import generate_discord_announcement_body, generate_discord_announcement_lineup, load_race_lineups_map, generate_race_lineup_json, generate_race_results_json

from typing import Dict, List, Optional
import argparse

def main(argv: Optional[List[str]] = None) -> None:
    TOTAL_HORSE = 18
    parser = argparse.ArgumentParser(description="Generate Discord announcement markdown for lineup")
    # parser.add_argument("--lineup-file", default="race_lineups/dummy_lineup.json")
    parser.add_argument("--url", default="https://en.netkeiba.com/race/shutuba.html?race_id=202609020411")
    parser.add_argument("--output-file", required=True, help="Enter a file name ending with .json. Default Output Directory is /race_lineups/")
    parser.add_argument("--output-dir", default="race_lineups", help="Output directory for the generated lineup JSON file. Default is /race_lineups/")

    args = parser.parse_args(argv)
    
    # generates a json file at /race_lineups/
    generate_race_lineup_json(args.url, args.output_file, args.output_dir)

    lineup_path = Path(args.output_dir) / args.output_file
    race_lineup = load_race_lineups_map(lineup_path)
    race_name = Path(lineup_path).stem
    body_markdown = generate_discord_announcement_body(race_name, args.url)
    lineup_markdown = generate_discord_announcement_lineup(race_lineup, TOTAL_HORSE, race_name)

    print("\n==================================")
    print("BELOW IS DISCORD MARKDOWN TO COPY")
    print("==================================\n")

    print(body_markdown)
    print(lineup_markdown)

if __name__ == "__main__":
    main()
