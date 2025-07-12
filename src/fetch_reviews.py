# # Paths
# CITY_FILE = "/Users/luigicheng/restaurant-recommender/data/review_cities.csv"
# CITY_DATA_DIR = "/Users/luigicheng/restaurant-recommender/data/cities"
# REVIEW_SAVE_DIR = "/Users/luigicheng/restaurant-recommender/data/reviews"
# PER_CITY_CSV_DIR = "/Users/luigicheng/restaurant-recommender/data/city_review"
# MAX_PAGES = 10

import os
import json
import time
import random
import pandas as pd
from tqdm import tqdm
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import TimeoutException, WebDriverException

# ==== PATHS ====
CITY_FILE = "/Users/luigicheng/restaurant-recommender/data/review_cities.csv"
CITY_DATA_DIR = "/Users/luigicheng/restaurant-recommender/data/cities"
REVIEW_SAVE_DIR = "/Users/luigicheng/restaurant-recommender/data/reviews"
PER_CITY_CSV_DIR = "/Users/luigicheng/restaurant-recommender/data/city_review"
MAX_PAGES = 10

# ==== DECODED PROXY INFO ====
PROXY_HOST = "gate.decodo.com"
PROXY_PORT = 10001
PROXY_USER = "spv05jbdtm"
PROXY_PASS = "rsVaLp5+0F0krwfQt7"

def configure_driver():
    proxy_argument = f"{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"

    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=http://{proxy_argument}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")

    return uc.Chrome(options=chrome_options)

def already_scraped(state, city, business_id):
    path = os.path.join(REVIEW_SAVE_DIR, state, city.replace(" ", "_"), f"{business_id}.json")
    return os.path.exists(path)

def scrape_reviews(driver, url, max_reviews=3):
    reviews = []
    try:
        driver.get(url)
        time.sleep(random.uniform(3, 6))

        review_elements = driver.find_elements(By.CSS_SELECTOR, "li [data-testid='review-comment'] p")
        for el in review_elements[:max_reviews]:
            reviews.append(el.text.strip())

        if not reviews:
            print("⚠️ No reviews found — maybe blocked or selector mismatch")

    except (TimeoutException, WebDriverException) as e:
        print(f"❌ Exception at {url}: {e}")

    return reviews

def save_reviews(state, city, business_id, reviews):
    out_dir = os.path.join(REVIEW_SAVE_DIR, state, city.replace(" ", "_"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{business_id}.json")
    with open(out_path, "w") as f:
        json.dump(reviews, f, indent=2)

def main():
    os.makedirs(PER_CITY_CSV_DIR, exist_ok=True)
    cities_df = pd.read_csv(CITY_FILE)
    pending = cities_df[cities_df["status"] == "pending"]

    driver = configure_driver()

    for idx, row in pending.iterrows():
        city, state = row["city"], row["state"]
        print(f"\n📍 Starting review scrape: {city}, {state}")

        filename = f"{state}_{city.replace(' ', '_')}_restaurants.csv"
        path = os.path.join(CITY_DATA_DIR, filename)
        if not os.path.exists(path):
            print(f"⚠️ File not found: {filename}")
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

            reviews = scrape_reviews(driver, url)
            if reviews:
                save_reviews(state, city, biz_id, reviews)
                for rev in reviews:
                    city_reviews.append({
                        "business_id": biz_id,
                        "name": biz.get("name"),
                        "city": city,
                        "state": state,
                        "review": rev
                    })

            time.sleep(random.uniform(2, 4))

        if city_reviews:
            city_df = pd.DataFrame(city_reviews)
            out_path = os.path.join(PER_CITY_CSV_DIR, f"{state}_{city.replace(' ', '_')}_reviews.csv")
            city_df.to_csv(out_path, index=False)
            print(f"💾 City reviews saved: {out_path} ({len(city_df)} reviews)")

        cities_df.at[idx, "status"] = "done"
        cities_df.to_csv(CITY_FILE, index=False)
        print(f"✅ Finished {city}, {state} — checkpoint saved.")

    driver.quit()
    print("\n🎉 All done scraping reviews.")

if __name__ == "__main__":
    main()