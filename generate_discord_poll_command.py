from pathlib import Path
from typing import Dict, List, Optional
from src.discord_formatter._core import load_race_lineups_map
from src.discord_formatter._core import fetch_timestamp
import argparse

def main(argv: Optional[List[str]] = None) -> None:
    # used in cases where the official lineup has more than 18 horses before it becomes official
    # Just take the top TOTAL_HORSE_ANSWER horses
    TOTAL_HORSE_ANSWER = 18

    parser = argparse.ArgumentParser(description="Generate Discord poll command from a single lineup")
    parser.add_argument("--lineup-file", required=True, help="Default path after running generate_discord_announcement.py is race_lineups. Exmaple value: race_lineups/Satsuki Sho.json")
    parser.add_argument("--url", required=True, help="URL must be from https://en.netkeiba.com. Example: https://en.netkeiba.com/race/shutuba.html?race_id=202606030811")

    args = parser.parse_args(argv)
    
    print("\n==================================")
    print("BELOW IS DISCORD COMMAND TO COPY")
    print("Manually copy the generated text and paste into discord")
    print("You may need to click the poll command, it should then auto format and accept the parameters")
    print("==================================\n")

    race_lineup = load_race_lineups_map(args.lineup_file)
    timestamp = fetch_timestamp(args.url)
    race_name = Path(args.lineup_file).stem

    command = "/timepoll"
    time = f"time:{timestamp}"
    question = f"question:Select 3 horses for the {race_name}"
    type = "type:Hidden (Select Menu)"
    maxchoices = "maxchoices:3"
    text = f"text:Who will win the {race_name}?"

    final_command = f"{command} {time} {question} {type} {maxchoices} {text} "

    # The poll command has a hard limit at 20
    # final lineup will be 18

    horse_list = list(race_lineup.keys())
    for index, horse in enumerate(horse_list[:TOTAL_HORSE_ANSWER]):
        final_command += f"answer-{index + 1}:{horse} "
    
    print("\n\n")
    print(final_command)
    print("\n\n")


if __name__ == "__main__":
    main()
