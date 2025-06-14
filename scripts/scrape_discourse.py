# scripts/scrape_discourse.py
import requests
import os
import json
from datetime import datetime, timezone
from urllib.parse import urljoin

# ========== CONFIGURATION ==========
# TODO: Fill these values before running the script
DISCOURSE_BASE_URL = "https://discourse.onlinedegree.iitm.ac.in/"
CATEGORY_SLUG = "courses/tds-kb" # Example, change to the correct one
CATEGORY_ID = 34                 # Example, change to the correct one
START_DATE = datetime.strptime("2025-01-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2025-04-14", "%Y-%m-%d")

OUTPUT_DIR = "data/discourse_json"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": settings.RAW_COOKIE_STRING
}

def get_all_topic_links():
    print("Fetching topic links...")
    topic_links = set()
    page = 0
    while True:
        url = f"{BASE_URL}{CATEGORY_SLUG}.json?page={page}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print("Failed to fetch", url)
            break
        data = resp.json()
        topics = data.get("topic_list", {}).get("topics", [])
        if not topics:
            break
        for topic in topics:
            slug = topic.get("slug")
            topic_id = topic.get("id")
            created_at = topic.get("created_at") or topic.get("last_posted_at")
            if slug and topic_id and created_at:
                try:
                    created_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        created_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                    except Exception as e:
                        print(f"Skipping malformed topic date: {created_at}")
                        continue
                if START_DATE <= created_dt <= END_DATE:
                    topic_links.add(f"t/{slug}/{topic_id}.json")
        page += 1
        sleep(1)
    print(f"Found {len(topic_links)} topics.")
    return topic_links


def download_topic(slug):
    url = urljoin(BASE_URL, slug)
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        topic_id = slug.split("/")[-1].replace(".json", "")
        with open(os.path.join(OUTPUT_DIR, f"{topic_id}.json"), "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"Downloaded topic {topic_id}")
    else:
        print(f"Failed to fetch topic: {url}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    topic_links = get_all_topic_links()
    for link in topic_links:
        download_topic(link)
        sleep(0.5)

if __name__ == "__main__":
    main()
