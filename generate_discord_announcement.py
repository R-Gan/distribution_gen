from pathlib import Path
from src.calc_results._core import load_file, build_answers_map, build_votes_map, calc_results_map
from src.discord_formatter._core import generate_discord_announcement_body, generate_discord_announcement_lineup, load_race_lineups_map

from typing import Dict, List, Optional
import argparse

def main(argv: Optional[List[str]] = None) -> None:
    TOTAL_HORSE = 18
    parser = argparse.ArgumentParser(description="Generate Discord announcement markdown for lineup")
    parser.add_argument("--lineup-file", default="race_lineups/dummy_lineup.json")
    parser.add_argument("--url", default="https://en.netkeiba.com/race/shutuba.html?race_id=202609020411")

    args = parser.parse_args(argv)
    
    race_lineup = load_race_lineups_map(args.lineup_file)
    race_name = Path(args.lineup_file).stem
    body_markdown = generate_discord_announcement_body(race_name, args.url)
    lineup_markdown = generate_discord_announcement_lineup(race_lineup, TOTAL_HORSE, race_name)

    print("\n==================================")
    print("BELOW IS DISCORD MARKDOWN TO COPY")
    print("==================================\n")

    print(body_markdown)
    print(lineup_markdown)

if __name__ == "__main__":
    main()
