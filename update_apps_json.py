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
APPS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "apps.json")

def scrape_app_ids():
    app_ids = set()
    
    print("Fetching using google_play_scraper search...")
    try:
        from google_play_scraper import search
        results = search("pub:ssteam")
        for app in results:
            if 'appId' in app:
                app_ids.add(app['appId'])
    except Exception as e:
        print(f"Error fetching apps via search: {e}")

    print("Fetching using raw HTML scraping...")
    urls = [DEV_URL, SEARCH_URL]
    for url in urls:
        print(f"Fetching: {url}")
        try:
            response = requests.get(url)
            # Find standard links
            matches = re.findall(r'details\?id=([a-zA-Z0-9._]+)', response.text)
            for m in matches:
                app_ids.add(m)
            
            # Find com.ssteam.* package names anywhere in the source (e.g. in script tags)
            ssteam_matches = re.findall(r'(com\.ssteam\.[a-zA-Z0-9._]+)', response.text)
            for m in ssteam_matches:
                app_ids.add(m)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    # Filter out potential false positives
    valid_ids = {aid for aid in app_ids if len(aid.split('.')) >= 2 and len(aid) < 100}
    
    print(f"Found {len(valid_ids)} unique potential app IDs.")
    return sorted(list(valid_ids))

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
