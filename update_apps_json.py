import json
import os
import re
import requests
from bs4 import BeautifulSoup

# Dependencies: pip install requests beautifulsoup4 google-play-scraper

try:
    from google_play_scraper import app as get_app_details
except ImportError:
    print("google-play-scraper not found. Installing...")
    os.system("pip install google-play-scraper")
    from google_play_scraper import app as get_app_details

DEV_URL = "https://play.google.com/store/apps/dev?id=8108163760101121306"
SEARCH_URL = "https://play.google.com/store/search?q=pub:ssteam&c=apps"
APPS_JSON_PATH = os.path.join("data", "apps.json")

def scrape_app_ids():
    app_ids = set()
    
    for url in [DEV_URL, SEARCH_URL]:
        print(f"Fetching: {url}")
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch {url}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links that look like app details
            for a in soup.find_all('a', href=True):
                href = a['href']
                match = re.search(r'details\?id=([a-zA-Z0-9._]+)', href)
                if match:
                    app_ids.add(match.group(1))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    print(f"Found {len(app_ids)} unique potential app IDs.")
    return sorted(list(app_ids))

def update_apps_json(app_ids):
    if not os.path.exists(APPS_JSON_PATH):
        existing_apps = []
    else:
        with open(APPS_JSON_PATH, 'r', encoding='utf-8') as f:
            try:
                existing_apps = json.load(f)
            except json.JSONDecodeError:
                existing_apps = []

    existing_ids = {app['id'] for app in existing_apps}
    updated_apps = {app['id']: app for app in existing_apps}

    new_apps_count = 0
    for app_id in app_ids:
        print(f"Processing {app_id}...")
        try:
            details = get_app_details(app_id)
            app_data = {
                "id": app_id,
                "name": details['title'],
                "icon": details['icon']
            }
            
            if app_id not in updated_apps:
                new_apps_count += 1
                print(f"  + New app: {details['title']}")
            else:
                # Update existing if needed (e.g. icon might change)
                pass
            
            updated_apps[app_id] = app_data
        except Exception as e:
            print(f"  - Error fetching details for {app_id}: {e}")

    # Convert back to list and sort by name
    final_apps_list = sorted(updated_apps.values(), key=lambda x: x['name'])

    with open(APPS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_apps_list, f, indent=4, ensure_ascii=False)

    print(f"Done! Updated {APPS_JSON_PATH}.")
    print(f"Total apps: {len(final_apps_list)} ({new_apps_count} new)")

if __name__ == "__main__":
    ids = scrape_app_ids()
    if ids:
        update_apps_json(ids)
    else:
        print("No app IDs found. Scraper might need updating.")
