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
START_DATE = "2025-01-01"
END_DATE = "2025-04-14"

# IMPORTANT: You must get this from your browser's developer tools
# after logging into the Discourse forum.
RAW_COOKIE_STRING = """_t=t6FF36OXglAFObbbywp%2B8II9dI%2Bu2W76grWNAPN%2B3bDGNoGhPtt5sr%2B%2BEng0B4J8AHPNG8ewPsF3r6KR1SWlZpVK%2Fmy77tyRofaGh976spnts8hRu6xdyIPFPKDjaaIJPQ4Ez4UfkHJSAa4vxvWOGFIJpWUP9vUUwvBZWN%2Beg7rAmqeCnM9mX3bPZ2yFEXy7iLnNFz5S6MDu%2Br%2F9asEB4DLAxRiRj2x7ima11QANaNNfdUVY7n0XVfpDTqBfbyRyJTBjPyz83z9tivlwA51YD0RFC%2FqM5gfv9n84Elt60jnDBmR0OXcLMvLzBxt5veTR--nf%2F%2BrgVzKC1D0eUb--av9ctizknls2meXuLiWQKA%3D%3D; _bypass_cache=true; _forum_session=zT7IfI72nGxEqhHX9Pn5Cxkv9NrpqZAWF21Hq9Ore7o3YEjEwf03ziSY058qN3hG%2B%2BBw25GTs%2BwArE%2FDaDgj0y7%2BTVUjlUxT%2Fd1W1S3y2VrzxSZArPGNXbswXhqk58nycva5bK6bMUe%2B0ikZJ82zwk4L3rHRW3enicgW3Uu5HCvFNq%2BaROV%2BxS7oqZ7%2BsCtoqtYEqpB3%2BF506LyF1D540gI6xuW%2BjfEru1AJ6IRIac6zSnotI9fl9Rvl71Fkz%2F22c%2BRtjQxS%2F5xhPvEDmH3%2F33SPfazbSq3fwx%2BcS%2BWZx1uUYqwkaAkuTKFFXWf7RSGRhQI81QiNGJcL%2FgsFrMSpElawzum3sMAxEFNeqtAsmWnWkWtL%2Fqwo0NXXBzconA%3D%3D--KZQACqPT0JQ82guq--Uv9vng8xPbGD2m7bfSavoQ%3D%3D""" # Replace with your actual cookie

# This script will save files into ../data/discourse_json/
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'discourse_json')

POST_ID_BATCH_SIZE = 50
MAX_CONSECUTIVE_PAGES_WITHOUT_NEW_TOPICS = 5

def parse_cookie_string(raw_cookie_string):
    cookies = {}
    for cookie in raw_cookie_string.split(";"):
        if "=" in cookie:
            key, value = cookie.strip().split("=", 1)
            cookies[key] = value
    return cookies

def get_topic_ids():
    start_dt = datetime.fromisoformat(START_DATE + "T00:00:00").replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(END_DATE + "T23:59:59").replace(tzinfo=timezone.utc)
    cookies = parse_cookie_string(COOKIE_STRING)

    topic_ids = []
    page = 0
    while True:
        url = f"{BASE_URL}/c/{CATEGORY_SLUG}/{CATEGORY_ID}.json?page={page}"
        res = requests.get(url, cookies=cookies, timeout=30)
        if res.status_code != 200:
            break
        data = res.json()
        topics = data.get("topic_list", {}).get("topics", [])
        if not topics:
            break
        for topic in topics:
            created = topic.get("created_at")
            if not created:
                continue
            created_at = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if start_dt <= created_at <= end_dt:
                topic_ids.append(topic["id"])
        page += 1
    return list(set(topic_ids))

def fetch_topic(topic_id):
    cookies = parse_cookie_string(COOKIE_STRING)
    url = f"{BASE_URL}/t/{topic_id}.json"
    res = requests.get(url, cookies=cookies, timeout=30)
    if res.status_code != 200:
        return None
    topic_data = res.json()

    all_post_ids = topic_data.get("post_stream", {}).get("stream", [])
    fetched_ids = {p["id"] for p in topic_data["post_stream"]["posts"]}
    missing_ids = [pid for pid in all_post_ids if pid not in fetched_ids]

    for i in range(0, len(missing_ids), 50):
        post_url = f"{BASE_URL}/t/{topic_id}/posts.json"
        params = [("post_ids[]", pid) for pid in missing_ids[i:i + 50]]
        r = requests.get(post_url, cookies=cookies, params=params, timeout=30)
        if r.status_code == 200:
            posts = r.json().get("post_stream", {}).get("posts", [])
            topic_data["post_stream"]["posts"].extend(posts)
    return topic_data

def save_topic(topic_id, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"topic_{topic_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("Fetching topic IDs...")
    ids = get_topic_ids()
    print(f"Found {len(ids)} topics.")
    for i, tid in enumerate(ids, 1):
        print(f"[{i}/{len(ids)}] Fetching topic {tid}...")
        data = fetch_topic(tid)
        if data:
            save_topic(tid, data)
    print("Scraping complete.")

if __name__ == "__main__":
    main()
