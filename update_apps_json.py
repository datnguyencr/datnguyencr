import json
import os
import re
import sys
import requests

# Dependencies check
try:
    from google_play_scraper import app as get_app_details
    from google_play_scraper import search
except ImportError:
    print("Required packages not found. Installing...")
    os.system(f"{sys.executable} -m pip install google-play-scraper requests")
    from google_play_scraper import app as get_app_details
    from google_play_scraper import search

DEV_ID = "8108163760101121306"
DEV_URL = f"https://play.google.com/store/apps/dev?id={DEV_ID}"
SEARCH_URL = "https://play.google.com/store/search?q=pub:ssteam&c=apps"
APPS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "apps.json")

def extract_package_names(html_content):
    """
    Finds all valid Android package names matching com.ssteam.
    Uses precise boundary matching to catch IDs embedded inside JSON blobs.
    """
    pattern = r'\bcom\.ssteam\.[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*\b'
    matches = re.findall(pattern, html_content)
    link_matches = re.findall(r'details\?id=([a-zA-Z0-9._]+)', html_content)
    return set(matches + link_matches)

def scrape_app_ids():
    app_ids = set()
    
    # 1. Clean & Safe Search query using google-play-scraper
    print("Fetching using google_play_scraper search...")
    try:
        # Search for the exact developer filter phrase
        results = search("pub:ssteam")
        if isinstance(results, list):
            for app in results:
                if app and isinstance(app, dict) and 'appId' in app:
                    app_ids.add(app['appId'])
    except Exception as e:
        print(f"  - Search query warning: {e}")

    # 2. Deep Script Parsing from the Raw HTML (Dev page & Search page)
    print("Fetching using Deep HTML & script block parsing...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    for url in [DEV_URL, SEARCH_URL]:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                found_packages = extract_package_names(response.text)
                app_ids.update(found_packages)
        except Exception as e:
            print(f"  - Error pulling HTML from {url}: {e}")
            
    # Filter list: Ensure they look like real package formats and belong to ssteam
    valid_ids = {
        aid for aid in app_ids 
        if len(aid.split('.')) >= 3 
        and len(aid) < 100 
        and 'ssteam' in aid.lower()
    }
    
    print(f"Found {len(valid_ids)} unique potential app IDs.")
    return sorted(list(valid_ids))

def update_apps_json(app_ids):
    # Ensure data folder directory path exists
    os.makedirs(os.path.dirname(APPS_JSON_PATH), exist_ok=True)

    if not os.path.exists(APPS_JSON_PATH):
        existing_apps = []
    else:
        with open(APPS_JSON_PATH, 'r', encoding='utf-8') as f:
            try:
                existing_apps = json.load(f)
            except json.JSONDecodeError:
                existing_apps = []

    updated_apps = {app['id']: app for app in existing_apps}
    new_apps_count = 0

    for app_id in app_ids:
        print(f"Processing {app_id}...")
        try:
            details = get_app_details(app_id)
            app_data = {
                "id": app_id,
                "name": details.get('title', 'Unknown Name'),
                "icon": details.get('icon', '')
            }
            
            if app_id not in updated_apps:
                new_apps_count += 1
                print(f"  + New app discovered: {app_data['name']}")
            
            updated_apps[app_id] = app_data
        except Exception as e:
            # If an app is unlisted or region-locked to your current IP, skip cleanly
            print(f"  - Skipping {app_id}: {e}")

    # Sort alphabetically by application name
    final_apps_list = sorted(updated_apps.values(), key=lambda x: x['name'].lower())

    with open(APPS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_apps_list, f, indent=4, ensure_ascii=False)

    print(f"\nDone! Updated {APPS_JSON_PATH}.")
    print(f"Total tracked apps: {len(final_apps_list)} ({new_apps_count} new this run)")

if __name__ == "__main__":
    ids = scrape_app_ids()
    if ids:
        update_apps_json(ids)
    else:
        print("No app IDs found. Check network connection or proxy settings.")