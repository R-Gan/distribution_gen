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
