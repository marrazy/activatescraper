import json
import re
from pathlib import Path

food_patterns = [
    "free food",
    "free complimentary drink",
    "food and refreshments provided",
    "food and refreshments",
    "food will be provided",
    "food is provided",
    "food provided",
    "food and drinks included",
    "food and drinks",
    "complimentary food",
    "complimentary food/drink",
    "refreshments provided",
    "included in ticket",
    "ticket includes food",
    "tickets include food",
    "food included",
    "food will be catered",
    "catered food",
    "bbq food",
    "pizza included",
    "meal included",
    "food and one drink ticket",
    "one drink ticket will be provided",
]


def clean_html(text):
    text = text or ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&#8217;", "'")
    text = text.replace("&amp;", " and ")
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def event_has_food_included(event):
    text = ""
    text += " " + (event.get("title") or "")
    text += " " + (event.get("desc") or "")
    text += " " + (event.get("price") or "")
    cleaned = clean_html(text)
    return any(p in cleaned for p in food_patterns)


def find_food_events(json_path="data/latest.json"):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    matches = []

    for club in data.get("clubs", []):
        for event in club.get("events") or []:
            if event_has_food_included(event):
                matches.append({
                    "club": club.get("name"),
                    "event": event.get("title"),
                    "url": event.get("url"),
                    "matched": next(p for p in food_patterns if p in clean_html(f"{event.get('title') or ''} {event.get('desc') or ''} {event.get('price') or ''}")),
                })

    return matches


if __name__ == "__main__":
    matches = find_food_events()
    print(f"Found {len(matches)} events with free/included food")
    for item in matches[:20]:
        print(f"- {item['club']} :: {item['event']} :: {item['matched']}")
        print(f"  {item['url']}")

