import json
from pathlib import Path
from typing import Mapping, Optional, Union

def load_username_override_map(path: Union[str, Path]) -> Mapping[str, str]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object username->displayname")
    return {str(k): str(v) for k, v in data.items()}

def load_race_lineups_map(path: Union[str, Path]) -> Mapping[str, Mapping[str, Mapping[str, str]]]:
    p = Path(path)
    if not p.is_dir():
        return {}
    lineups = {}
    for file in p.glob('*.json'):
        race = file.stem
        with file.open('r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"{file} must contain a JSON object horse->{{odds, favorite}}")
        lineups[race] = {str(k): v for k, v in data.items()}
    return lineups

def generate_discord_announcement_markdown(race_lineups: Mapping[str, Mapping[str, Mapping[str, str]]], total_horses: int) -> str:
    lines = ["**Upcoming Race Lineups:**\n"]

    for race, lineup in race_lineups.items():
        curr_max = 0
        for horse in lineup.keys():
            curr_max = max(curr_max, len(horse))

        lines.append(f"**{race}:**\n")
        horse_padding = " " * (curr_max - len("horse") + 1)
        fav_padding = " " * (5 - len("fav") + 1)
        odds_padding = " " * (5 - len("odds") + 1)
        header = f"```horse{horse_padding}|fav{fav_padding}|odds{odds_padding}"
        lines.append(header)
        lines.append("+" * len(header))
        horses = sorted(lineup.items(), key=lambda x: int(x[1]['favorite']))
        for horse, data in horses[:total_horses]:
            odds = data['odds']
            fav = data['favorite']
            horse_padding = " " * (curr_max - len(horse) + 2)
            fav_padding = " " * (5 - len(fav) + 2)
            odds_padding = " " * (5 - len(odds) + 2)
            lines.append(f"{horse}{horse_padding}{fav}{fav_padding}{odds}{odds_padding}")
        lines.append("```")
    return "\n".join(lines)

def generate_discord_markdown(
    points_map: Mapping[str, float],
    override_map: Optional[Mapping[str, str]] = None
) -> str:
    override_map = override_map or {}
    currMax = 0
    for username in points_map.keys():
        if username in override_map:
            currMax = max(currMax, len(override_map[username]))
            print(f"Username '{username}' has display name '{override_map[username]}'")
        else:
            currMax = max(currMax, len(username))
            print(f"Username '{username}' has no display name override, using raw username")

    sorted_users = sorted(
        points_map.items(),
        key=lambda item: item[1],
        reverse=True
    )

    lines = ["**Poll Results:**\n"]

    for username, points in sorted_users:
        display_name = override_map.get(username) or username
        # handle odd discord font spacing
        if (len(display_name) == currMax):
            padding = "-" * (currMax - len(display_name) + 2)
        else:
            padding = "-" * (currMax - len(display_name) + 3)
        lines.append(f"@{username} {padding} {points:.2f} points")

    return "\n".join(lines)

def main():
    print("discord formatter main")

if __name__ == "__main__":
    main()
