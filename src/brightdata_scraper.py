import requests
import json
import time

API_TOKEN = "d0fe6420bf15c0437b8ae25372f9622c3ad36b3b244363eaf9e3dfa5b4643c66"
COLLECTOR_ID = "gd_lgzhlu9323u3k24jkv"
API_URL = f"https://scraperapi.brightdata.com/dca/trigger?collector={COLLECTOR_ID}"

# Yelp URLs to scrape
yelp_urls = [
    "https://www.yelp.com/biz/tumbys-pizza-inglewood",
    "https://www.yelp.com/biz/fratellis-pizza-los-angeles-4",
    "https://www.yelp.com/biz/pepes-ny-pizza-studio-city"
]

results = []

for url in yelp_urls:
    print(f"📤 Triggering scrape for: {url}")
    payload = {
        "url": url
    }

    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ Failed: {response.text}")
        continue

    job_info = response.json()
    job_id = job_info.get("collection_id")

    print(f"⏳ Waiting for job to finish (ID: {job_id})...")

    # Poll job status
    status_url = f"https://scraperapi.brightdata.com/dca/collector_status?collection_id={job_id}"

    while True:
        status_res = requests.get(
            status_url,
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        ).json()

        if status_res.get("status") == "done":
            print(f"✅ Done: {url}")
            result_url = status_res.get("result_url")
            data = requests.get(result_url).json()
            results.append({"url": url, "reviews": data})
            break

        elif status_res.get("status") == "error":
            print(f"❌ Job error for {url}")
            break

        time.sleep(5)

# Save to file
with open("yelp_reviews_brightdata.json", "w") as f:
    json.dump(results, f, indent=2)

print("📁 All reviews saved to 'yelp_reviews_brightdata.json'")