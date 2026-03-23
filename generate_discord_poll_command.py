from typing import Dict, List, Optional
from src.discord_formatter._core import load_race_lineups_map
import argparse

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Calculate poll results into point allocations")
    parser.add_argument("--poll-file", default="json_poll/test_poll.json")
    parser.add_argument("--results-file", default="live_results/results.json")
    parser.add_argument("--point-pool", type=int, default=100)

    args = parser.parse_args(argv)
    
    print("\n==================================")
    print("BELOW IS DISCORD COMMAND TO COPY")
    print("Manually copy the generated text and paste into discord")
    print("You may need to click the poll command, it should then auto format and accept the parameters")
    print("==================================\n")

# /poll question:Who will win the 2026 Takamatsunomiya Kinen? type:Hidden (Select Menu) maxchoices:3 text:Who will win the 2026 Takamatsunomiya Kinen?

    race_lineups = load_race_lineups_map("race_lineups")

    command = "/poll"
    question = "question:Select 3 horses for the 2026 Takamatsunomiya Kinen"
    type = "type:Hidden (Select Menu)"
    maxchoices = "maxchoices:3"
    text = "text:Who will win the 2026 Takamatsunomiya Kinen?"

    final_command = f"{command} {question} {type} {maxchoices} {text} "

    horse_list = race_lineups.get("2026TAKAMATSUNOMIYA_KINEN", {}).keys()
    for index, horse in enumerate(horse_list):
        final_command += f"answer-{index + 1}:{horse} "
    
    print("\n\n")
    print(final_command)
    print("\n\n")


if __name__ == "__main__":
    main()
