import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Mapping, Optional, Union
from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright

def load_username_override_map(path: Union[str, Path]) -> Mapping[str, str]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object username->displayname")
    return {str(k): str(v) for k, v in data.items()}

def generate_race_results_json(url: str, outfile: str, outdir: str = "live_results") -> Mapping[str, Mapping[str, str]]:
    res = requests.get(url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    data = []

    links = soup.select(".Horse_Name a")

    for link in links:
        horse_name = link.get_text(strip=True)
        data.append(horse_name)

    json_data = {
        "results": data
    }
    json_output = json.dumps(json_data, ensure_ascii=False, indent=4)

    print(data)

    output_path = Path(outdir) / outfile
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_output)
    return data

def generate_race_lineup_json(url: str, outfile: str, outdir: str = "race_lineups") -> Mapping[str, Mapping[str, str]]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(".HorseList")
        page.wait_for_selector(".Popular")
        page.wait_for_selector(".Fav")
        pw_links = page.query_selector_all(".HorseList a")
        data = {}
        for link in pw_links:
            horse_name = link.inner_text().strip()
            horse_list = link.evaluate_handle("el => el.closest('.HorseList')")
            odds_elem = horse_list.query_selector(".Popular span")
            odds_text = odds_elem.inner_text().strip() if odds_elem else ""
            fav_elem = horse_list.query_selector(".Fav span")
            favorite_text = fav_elem.inner_text().strip() if fav_elem else ""
            data[horse_name] = {
                "odds": odds_text,
                "favorite": favorite_text
            }

        json_output = json.dumps(data, ensure_ascii=False, indent=4)
        output_path = Path(outdir) / outfile
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_output)
        browser.close()
    return data

def build_unix_timestamp(year: int, day_month_text: str, time_text: str) -> int:
    JST_OFFSET_HOURS = 9
    TEN_MINUTES = 10

    month_map = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
        "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
        "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
    }

    day, month_text = day_month_text.strip().split(" ")
    hour, minute = map(int, time_text.strip().split(":"))
    month = month_map.get(month_text.upper())

    if not month:
        raise ValueError(f"Unrecognized month abbreviation: {month_text}")

    # Create datetime in JST
    jst = timezone(timedelta(hours=JST_OFFSET_HOURS))
    dt_jst = datetime(year, month, int(day), hour, minute, tzinfo=jst)

    # Convert to UTC
    dt_utc = dt_jst.astimezone(timezone.utc)

    # Subtract 10 minutes
    dt_utc -= timedelta(minutes=TEN_MINUTES)

    return int(dt_utc.timestamp())

def fetch_timestamp(url: str) -> str:
    res = requests.get(url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    # Extract "15 APR"
    day_month_elem = soup.select_one("dd.Active span.Day01")
    day_month_text = day_month_elem.get_text(strip=True)

    # Extract "15:40"
    race_data_elem = soup.select_one(".Race_Data")
    time_text = race_data_elem.get_text("\n").split("\n")[0].strip()

    year = datetime.now().year

    return build_unix_timestamp(year, day_month_text, time_text)



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
🏆 We'll update the scoreboard
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
[{racename}]({url})
'''.format(racename=race_name, url=url, date=123, time=123)
    
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

    # print(sorted_results)

    # Grab top N (default 3)
    return sorted_results[:n]

def aggregate_points(results):
    totals = defaultdict(float)

    for entry in results:
        for player, stats in entry["players"].items():
            totals[player] += stats["points"]

    # print(totals)

    return dict(totals)


def get_max_lengths(points_map, override_map):
    max_username_length = 0
    max_points_length = 0

    for username, points in points_map.items():
        display_name = override_map.get(username, username)
        max_username_length = max(max_username_length, len(display_name))
        max_points_length = max(max_points_length, len(f"{points:.2f}"))

    return max_username_length, max_points_length


def convert_wins_to_medals(wins):
    text = ""
    for index in range(wins):
        text += "🏅"
        if (index + 1) % 5 == 0:
            text += "\n"

    return text

def print_with_discord_username_tags(sorted_users, max_name_length, max_points_length, total_wins, override_map):
    lines = ["**Poll Results:**\n"]
    count = 1
    for username, points in sorted_users:
        display_name = override_map.get(username) or username
        # handle odd discord font spacing
        if (len(display_name) == max_name_length):
            name_padding = "-" * (max_name_length - len(display_name) + 2)
        else:
            name_padding = "-" * (max_name_length - len(display_name) + 3)
        points_padding = " " * (max_points_length - len(f"{points:.2f}") + 2)
        medals = convert_wins_to_medals(total_wins.get(username, 0)).split("\n")
        # lines.append(f"@{username} {padding}  {points_padding}{points:.2f} pts | 🏅 x{total_wins.get(username, 0)}")
        lines.append(f"{count}. @{username} {name_padding} {points_padding}{points:.2f} pts")
        for row in medals:
            lines.append(f"{row}")
        count += 1
    lines = "\n".join(lines) + "\n"
    return lines


def print_with_discord_displayname_monospace(sorted_users, max_name_length, max_points_length, total_wins, override_map):
    lines = ["**Poll Results:**\n"]
    lines.append("```")
    count = 1
    for username, points in sorted_users:
        display_name = override_map.get(username) or username
        name_padding = " " * (max_name_length - len(display_name))
        points_padding = " " * (max_points_length - len(f"{points:.2f}"))
        medals = convert_wins_to_medals(total_wins.get(username, 0)).split("\n")
        # lines.append(f"{display_name}{name_padding} {points_padding}{points:.2f} | 🏅 x{total_wins.get(username, 0)}")
        lines.append(f"{count}. {display_name}{name_padding} {points_padding}{points:.2f} pts")
        for row in medals:
            lines.append(f"{row}")
        count += 1
    lines = "\n".join(lines) + "\n```"
    return lines


def generate_discord_results_markdown(
    hall_of_fame_path: str,
    total_wins: Mapping[str, int],
    override_map: Optional[Mapping[str, str]] = None,
    sliding_window_size: int = 3
) -> str:
    override_map = override_map or {}
    with open(hall_of_fame_path, "r") as f:
        hall_of_fame_data = json.load(f)

    recent_results = get_most_recent_results(hall_of_fame_data, sliding_window_size)
    # print(recent_results)
    points_map = aggregate_points(recent_results)
    # print(points_map)

    max_name_length, max_points_length = get_max_lengths(points_map, override_map)

    sorted_users = sorted(
        points_map.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # markdown = print_with_discord_username_tags(sorted_users, max_name_length, max_points_length, total_wins, override_map)
    markdown = print_with_discord_displayname_monospace(sorted_users, max_name_length, max_points_length, total_wins, override_map)
    return markdown


def main():
    print("discord formatter main")

if __name__ == "__main__":
    main()
