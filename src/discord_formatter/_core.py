import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
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

def load_race_lineups_map(path: Union[str, Path]) -> Mapping[str, Mapping[str, str]]:
    p = Path(path)
    if not p.is_file():
        return {}
    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object horse->{{odds, favorite}}")
    return {str(k): v for k, v in data.items()}

def generate_discord_announcement_lineup(
    race_lineup: Mapping[str, Mapping[str, str]],
    total_horses: int,
    race_name: Optional[str] = None
) -> str:
    race_name = race_name or "Race Lineup"
    lines = ["**Upcoming Race Lineup:**\n"]

    curr_max = 0
    for horse in race_lineup.keys():
        curr_max = max(curr_max, len(horse))

    lines.append(f"**{race_name}:**\n")
    horse_padding = " " * (curr_max - len("horse") + 1)
    fav_padding = " " * (5 - len("fav") + 1)
    odds_padding = " " * (5 - len("odds") + 1)
    header = f"```horse{horse_padding}|fav{fav_padding}|odds{odds_padding}"
    lines.append(header)
    lines.append("+" * len(header))
    horses = sorted(race_lineup.items(), key=lambda x: int(x[1]['favorite']))
    for horse, data in horses[:total_horses]:
        odds = data['odds']
        fav = data['favorite']
        horse_padding = " " * (curr_max - len(horse) + 2)
        fav_padding = " " * (5 - len(fav) + 2)
        odds_padding = " " * (5 - len(odds) + 2)
        lines.append(f"{horse}{horse_padding}{fav}{fav_padding}{odds}{odds_padding}")
    lines.append("```")
    return "\n".join(lines)


def generate_discord_announcement_body(
    race_name: Optional[str] = None,
    url: Optional[str] = None,
) -> str:

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")



    title = soup.title.text
    print(f"Fetched title from {url}: {title}")

    markdown = '''
@DerbyUma

With the JRA now streaming races online, there was interest in watching races and guessing which horses will win.
So... we made a channel for exactly that!

📊 How it works
We'll post a poll for every G1 race from now until the end of the year
You can pick up to 3 horses per race
✨HINT: Use all 3 picks - every selection earns you points!✨
You are able to change your votes at any point through the poll itself.

The Hall of Fame leaderboard will track the last 3 scoring results. This means new participants will be able to compete with veteran participants after 2 or 3 races!

After each race:

🎊 We'll highlight those who picked the winner
🏆 We'll update the yearly scoreboard
📈 Everyone earns points - even if your picks finish last 😅 
🏁 Next Race Preview and new poll

Our next race race for the Tracen Hall of Fame:
📅 {racename}
🕒 {date} - {time} (Hong Kong time)
📏 1200m sprint
🐎 INSERT_NUM_HORSES horses competing

⭐ Horses to Watch
🥇 
🔥 
⚡ 

🔗 Race details & entries:
INSERTLINK
'''.format(racename=race_name, date=123, time=123)
    
    return markdown



def get_most_recent_results(data, n=3):
    def extract_date(entry):
        # Handle both "date" and the typo "data"
        date_str = entry.get("date") or entry.get("data")
        return datetime.strptime(date_str, "%Y-%m-%d")

    # Sort descending (most recent first)
    sorted_results = sorted(
        data["results"],
        key=extract_date,
        reverse=True
    )

    # Grab top N (default 3)
    return sorted_results[:n]

def aggregate_points(results):
    totals = defaultdict(float)

    for entry in results:
        for player, stats in entry["players"].items():
            totals[player] += stats["points"]

    # print(totals)

    return dict(totals)


def generate_discord_results_markdown_two(
    hall_of_fame_path: str,
    override_map: Optional[Mapping[str, str]] = None,
    sliding_window_size: int = 3
) -> str:
    override_map = override_map or {}
    with open(hall_of_fame_path, "r") as f:
        hall_of_fame_data = json.load(f)

    recent_results = get_most_recent_results(hall_of_fame_data, sliding_window_size)
    points_map = aggregate_points(recent_results)
    # print(points_map)

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

    # for r in recent_results:
    #     print(r.get("date") or r.get("data"))



def generate_discord_results_markdown(
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
