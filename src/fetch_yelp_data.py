import requests
import time
import pandas as pd
import os
from dotenv import load_dotenv

# Load Yelp API Key
load_dotenv()
API_KEY = os.getenv("YELP_API_KEY")
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

# Constants
SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
LIMIT = 50
DELAY = 1.0
MAX_API_CALLS = 4900
api_calls = 0

# Filters
price_levels = ["1", "2", "3", "4"]
categories = [
    "italian", "mexican", "chinese", "japanese", "sushi", "pizza", "burgers",
    "steak", "indian", "thai", "seafood", "bbq", "vegan", "breakfast"
]

# Load checkpoint CSV
checkpoint_path = "data/US_Major_Cities_Checkpoints.csv"
cities_df = pd.read_csv(checkpoint_path)
pending_cities = cities_df[cities_df["status"] == "pending"]

# Ensure output folder for per-city files
os.makedirs("data/cities", exist_ok=True)

# Function to fetch Yelp businesses
def fetch_businesses(city, state, price, category):
    global api_calls
    offset = 0
    results = []

    while api_calls < MAX_API_CALLS:
        params = {
            "location": f"{city}, {state}",
            "categories": category,
            "price": price,
            "limit": LIMIT,
            "offset": offset
        }
        response = requests.get(SEARCH_URL, headers=HEADERS, params=params)
        api_calls += 1

        if response.status_code != 200:
            print(f"❌ Error {response.status_code} for {city}, {state} | ${price} | {category} | offset={offset}")
            break

        data = response.json()
        businesses = data.get("businesses", [])
        if offset == 0:
            print(f"📍 {city}, {state} | ${price} | {category} → Yelp reports {data.get('total', '?')} businesses")

        if not businesses:
            break

        for biz in businesses:
            results.append({
                "id": biz.get("id"),
                "name": biz.get("name"),
                "url": biz.get("url"),
                "rating": biz.get("rating"),
                "review_count": biz.get("review_count"),
                "price": biz.get("price", ""),
                "latitude": biz["coordinates"].get("latitude"),
                "longitude": biz["coordinates"].get("longitude"),
                "address": ", ".join(biz["location"].get("display_address", [])),
                "city": city,
                "state": state,
                "price_level": price,
                "category": category,
                "categories": ", ".join([c["title"] for c in biz.get("categories", [])])
            })

        if len(businesses) < LIMIT:
            break
        offset += LIMIT
        time.sleep(DELAY)

    return results

# Main loop
all_results = []
for index, row in pending_cities.iterrows():
    city, state = row["city"], row["state"]
    print(f"\n🚀 Starting: {city}, {state}")

    city_results = []
    for price in price_levels:
        for category in categories:
            if api_calls >= MAX_API_CALLS:
                print("⚠️ API limit reached — stopping early.")
                break
            chunk = fetch_businesses(city, state, price, category)
            city_results.extend(chunk)

    # Save per-city file
    city_df = pd.DataFrame(city_results)
    filename = f"data/cities/{state}_{city.replace(' ', '_')}_restaurants.csv"
    city_df.to_csv(filename, index=False)
    print(f"💾 Saved: {filename} ({len(city_df)} records)")

    # Add to combined dataset
    all_results.extend(city_results)

    # Mark city as completed
    cities_df.at[index, "status"] = "done"
    cities_df.to_csv(checkpoint_path, index=False)
    print(f"✅ Finished: {city}, {state} — checkpoint saved.")

    if api_calls >= MAX_API_CALLS:
        break

# Save final combined CSV
df = pd.DataFrame(all_results)
os.makedirs("data", exist_ok=True)
df.to_csv("data/all_scraped_restaurants.csv", index=False)
print(f"\n🎉 All done. Saved {len(df)} total records.")
print(f"🔢 Total API calls used: {api_calls}")