import os
import time
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Constants
HEADERS = {"User-Agent": "Mozilla/5.0"}
CITY_FILE = "/Users/luigicheng/restaurant-recommender/data/review_cities.csv"
CITY_DATA_DIR = "/Users/luigicheng/restaurant-recommender/data/cities"
REVIEW_SAVE_DIR = "/Users/luigicheng/restaurant-recommender/data/reviews"
PER_CITY_CSV_DIR = "/Users/luigicheng/restaurant-recommender/data/city_review"
MAX_PAGES = 10

def scrape_reviews_from_url(url, max_pages=10):
    reviews = []
    for offset in range(0, max_pages * 10, 10):
        resp = requests.get(f"{url}?start={offset}", headers=HEADERS)
        if resp.status_code != 200:
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        review_blocks = soup.select("p.comment__09f24__gu0rG")
        if not review_blocks:
            break
        for block in review_blocks:
            reviews.append(block.get_text(strip=True))
        time.sleep(1.5)
    return reviews

def save_reviews(state, city, business_id, reviews):
    out_dir = os.path.join(REVIEW_SAVE_DIR, state, city.replace(" ", "_"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{business_id}.json")
    with open(out_path, "w") as f:
        json.dump(reviews, f, indent=2)

def already_scraped(state, city, business_id):
    path = os.path.join(REVIEW_SAVE_DIR, state, city.replace(" ", "_"), f"{business_id}.json")
    return os.path.exists(path)

# Ensure output folder for merged city reviews
os.makedirs(PER_CITY_CSV_DIR, exist_ok=True)

# Load city checkpoint file
cities_df = pd.read_csv(CITY_FILE)
pending = cities_df[cities_df["status"] == "pending"]

# Loop through each pending city
for idx, row in pending.iterrows():
    city, state = row["city"], row["state"]
    print(f"\n📍 Starting review scrape: {city}, {state}")

    filename = f"{state}_{city.replace(' ', '_')}_restaurants.csv"
    path = os.path.join(CITY_DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"⚠️ Skipping {city}, file not found: {filename}")
        continue

    df = pd.read_csv(path)
    if "url" not in df.columns:
        print(f"⚠️ Skipping {city}, missing 'url' column")
        continue

    city_reviews = []

    for _, biz in tqdm(df.iterrows(), total=len(df)):
        biz_id = biz["id"]
        url = biz.get("url")
        if not url or pd.isna(url) or already_scraped(state, city, biz_id):
            continue

        reviews = scrape_reviews_from_url(url, max_pages=MAX_PAGES)
        save_reviews(state, city, biz_id, reviews)

        for review in reviews:
            city_reviews.append({
                "business_id": biz_id,
                "name": biz.get("name"),
                "city": city,
                "state": state,
                "review": review
            })

    # Save merged city review CSV
    if city_reviews:
        review_df = pd.DataFrame(city_reviews)
        city_csv = os.path.join(PER_CITY_CSV_DIR, f"{state}_{city.replace(' ', '_')}_reviews.csv")
        review_df.to_csv(city_csv, index=False)
        print(f"💾 City review file saved: {city_csv} ({len(review_df)} reviews)")

    # ✅ Mark city as done and update CSV
    cities_df.at[idx, "status"] = "done"
    cities_df.to_csv(CITY_FILE, index=False)
    print(f"✅ Finished: {city}, {state} — checkpoint updated.")

print("\n✅ Done scraping all reviews and saving per-city files.")