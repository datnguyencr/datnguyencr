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

# Verified list of all known app IDs. Google Play's developer page uses JavaScript
# lazy-loading behind a "Show more" button that HTTP scraping cannot trigger, so some
# apps are consistently missed by scraping alone. This list ensures completeness.
# Update this set when publishing new apps.
KNOWN_APP_IDS = {
    "com.ssteam.algorithm_visualization",
    "com.ssteam.animal_connect",
    "com.ssteam.api_forge",
    "com.ssteam.apk_extractor",
    "com.ssteam.app_lock",
    "com.ssteam.aqua_guppy",
    "com.ssteam.audio_recorder",
    "com.ssteam.battery_info",
    "com.ssteam.blood_sugar_monitor",
    "com.ssteam.boucingball",
    "com.ssteam.brick_game",
    "com.ssteam.bubble_level",
    "com.ssteam.chess",
    "com.ssteam.chess_clock",
    "com.ssteam.color_mixer",
    "com.ssteam.compass",
    "com.ssteam.country_flags",
    "com.ssteam.crochet_pattern_maker",
    "com.ssteam.cube_solver",
    "com.ssteam.cv_builder",
    "com.ssteam.d2_items",
    "com.ssteam.d2_tools",
    "com.ssteam.d2_wiki",
    "com.ssteam.daily_wallpaper",
    "com.ssteam.device_info",
    "com.ssteam.easy_note",
    "com.ssteam.event_reminder",
    "com.ssteam.game_of_life",
    "com.ssteam.gif_wallpaper",
    "com.ssteam.gplx",
    "com.ssteam.gridtool",
    "com.ssteam.hide_files_calculator",
    "com.ssteam.hide_files_contact",
    "com.ssteam.interest_calculator",
    "com.ssteam.iq_test",
    "com.ssteam.jigsaw_puzzle",
    "com.ssteam.led_pixel_display",
    "com.ssteam.live_wallpaper",
    "com.ssteam.lol_build",
    "com.ssteam.lol_wiki",
    "com.ssteam.luna_calendar",
    "com.ssteam.maze_puzzle",
    "com.ssteam.medicinal_herbs",
    "com.ssteam.memory_test",
    "com.ssteam.mewpedia",
    "com.ssteam.minimal_clock",
    "com.ssteam.money_manager",
    "com.ssteam.notification_history",
    "com.ssteam.pattern_canvas",
    "com.ssteam.pattern_maker",
    "com.ssteam.pawpedia",
    "com.ssteam.periodic_table",
    "com.ssteam.photo_widget",
    "com.ssteam.pixeldrawer",
    "com.ssteam.planet_explorer",
    "com.ssteam.poe_divination_card",
    "com.ssteam.poe_wiki",
    "com.ssteam.poecurrency",
    "com.ssteam.pokemon_card_maker",
    "com.ssteam.pregnancy_tracker",
    "com.ssteam.protractor",
    "com.ssteam.qr_manager",
    "com.ssteam.rainsimulator",
    "com.ssteam.random_generator",
    "com.ssteam.reduce_image",
    "com.ssteam.reflex_game",
    "com.ssteam.screen_recorder",
    "com.ssteam.screenshot",
    "com.ssteam.sliding_puzzle",
    "com.ssteam.smart_light",
    "com.ssteam.sound_level",
    "com.ssteam.speed_test",
    "com.ssteam.stock_simulator",
    "com.ssteam.sudoku",
    "com.ssteam.tetrix",
    "com.ssteam.tictactoe",
    "com.ssteam.wifi_analyzer",
    "com.ssteam.yugioh_card_builder",
    "com.ssteam.yugioh_deck_builder",
}

def extract_package_names(html_content):
    """
    Finds all valid Android package names matching com.ssteam.
    Uses precise boundary matching to catch IDs embedded inside JSON blobs.
    """
    pattern = r'\bcom\.ssteam\.[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*\b'
    matches = re.findall(pattern, html_content)
    link_matches = re.findall(r'details\?id=([a-zA-Z0-9._]+)', html_content)
    return set(matches + link_matches)

def load_existing_app_ids():
    """Load app IDs already tracked in apps.json so we never lose them."""
    if not os.path.exists(APPS_JSON_PATH):
        return set()
    try:
        with open(APPS_JSON_PATH, 'r', encoding='utf-8') as f:
            existing_apps = json.load(f)
            return {app['id'] for app in existing_apps if 'id' in app}
    except (json.JSONDecodeError, KeyError):
        return set()

def scrape_app_ids():
    app_ids = set()
    
    # 0a. Start with all known/verified app IDs
    app_ids.update(KNOWN_APP_IDS)
    print(f"Loaded {len(KNOWN_APP_IDS)} known app IDs.")
    
    # 0b. Preserve all existing app IDs from apps.json (never lose already-discovered apps)
    existing_ids = load_existing_app_ids()
    if existing_ids:
        app_ids.update(existing_ids)
    
    # 1. Search using google-play-scraper with multiple queries and locales
    print("Fetching using google_play_scraper search...")
    search_queries = ["pub:ssteam", "ssteam", "com.ssteam"]
    locales = [
        {"lang": "en", "country": "us"},
        {"lang": "vi", "country": "vn"},
        {"lang": "en", "country": "gb"},
    ]
    
    for query in search_queries:
        for locale in locales:
            try:
                results = search(
                    query,
                    lang=locale["lang"],
                    country=locale["country"],
                    n_hits=100
                )
                if isinstance(results, list):
                    for app in results:
                        if app and isinstance(app, dict) and 'appId' in app:
                            app_ids.add(app['appId'])
            except Exception as e:
                print(f"  - Search '{query}' ({locale['country']}): {e}")

    # 2. Deep Script Parsing from the Raw HTML (Dev page & Search page)
    print("Fetching using Deep HTML & script block parsing...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8"
    }
    
    html_urls = [
        DEV_URL,
        SEARCH_URL,
        f"https://play.google.com/store/apps/dev?id={DEV_ID}&hl=vi",
        f"https://play.google.com/store/apps/dev?id={DEV_ID}&hl=en&gl=us",
        "https://play.google.com/store/apps/developer?id=ssteam",
        "https://play.google.com/store/search?q=ssteam&c=apps",
    ]
    
    for url in html_urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                found_packages = extract_package_names(response.text)
                app_ids.update(found_packages)
        except Exception as e:
            print(f"  - Error pulling HTML from {url}: {e}")
            
    # Filter list: Ensure they look like real package formats and belong to ssteam
    # Also exclude false positives that are actually file paths (e.g., .png, .jpg)
    file_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.xml', '.json', '.html', '.css', '.js'}
    valid_ids = {
        aid for aid in app_ids 
        if len(aid.split('.')) >= 3 
        and len(aid) < 100 
        and 'ssteam' in aid.lower()
        and not any(aid.lower().endswith(ext) for ext in file_extensions)
    }
    
    print(f"Found {len(valid_ids)} unique potential app IDs ({len(valid_ids) - len(existing_ids)} new from scraping).")
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