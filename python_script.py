import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup
import requests


# === CONFIG ===
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_ID = 34
CATEGORY_JSON_URL = f"{BASE_URL}/c/courses/tds-kb/{CATEGORY_ID}.json"
AUTH_STATE_FILE = "auth.json"
COOKIES_FILE = "cookies.json"
DATE_FROM = datetime(2025, 1, 1)
DATE_TO = datetime(2025, 4, 14)


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")


def login_and_save_auth(playwright):
    """Manual login via Playwright and save cookies"""
    print("🔐 No auth found. Launching browser for manual login...")
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{BASE_URL}/login")
    print("🌐 Please log in manually using Google. Then press ▶️ (Resume) in Playwright bar.")
    page.pause()
    
    # Save full storage state
    context.storage_state(path=AUTH_STATE_FILE)
    
    # Extract and save cookies separately
    cookies = context.cookies()
    with open(COOKIES_FILE, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print("✅ Login state and cookies saved.")
    browser.close()


def extract_cookies_from_storage_state():
    """Extract cookies from Playwright storage_state file"""
    if os.path.exists(AUTH_STATE_FILE):
        with open(AUTH_STATE_FILE, 'r') as f:
            storage_state = json.load(f)
        cookies = storage_state.get('cookies', [])
        
        with open(COOKIES_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"✅ Extracted {len(cookies)} cookies from storage state")
        return cookies
    return []


def load_cookies_for_requests():
    """Load cookies from file and convert to requests format"""
    if not os.path.exists(COOKIES_FILE):
        return {}
    
    with open(COOKIES_FILE, 'r') as f:
        playwright_cookies = json.load(f)
    
    # Convert Playwright cookie format to requests format
    cookies_dict = {}
    for cookie in playwright_cookies:
        # Filter cookies for the target domain
        if BASE_URL.replace('https://', '').replace('http://', '') in cookie.get('domain', ''):
            cookies_dict[cookie['name']] = cookie['value']
    
    return cookies_dict


def is_authenticated_with_cookies(session):
    """Check if cookies are valid by making a test request"""
    try:
        response = session.get(CATEGORY_JSON_URL, timeout=10)
        if response.status_code == 200:
            response.json()  # Validate JSON response
            return True
    except (requests.RequestException, json.JSONDecodeError):
        return False
    return False


def scrape_posts_with_requests():
    """Scrape posts using requests library with cookies"""
    print("🔍 Starting scrape using saved cookies...")
    
    # Create requests session
    session = requests.Session()
    
    # Load cookies
    cookies = load_cookies_for_requests()
    if not cookies:
        print("❌ No cookies found. Please authenticate first.")
        return
    
    # Set cookies and headers
    session.cookies.update(cookies)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    
    # Check authentication
    if not is_authenticated_with_cookies(session):
        print("⚠️ Cookies invalid or expired. Please re-authenticate.")
        return
    
    print("✅ Authenticated successfully with cookies")
    
    all_topics = []
    page_num = 0
    
    while True:
        paginated_url = f"{CATEGORY_JSON_URL}?page={page_num}"
        print(f"📦 Fetching page {page_num}...")
        
        try:
            response = session.get(paginated_url, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"❌ Error fetching page {page_num}: {e}")
            break
        
        topics = data.get("topic_list", {}).get("topics", [])
        if not topics:
            break
        
        all_topics.extend(topics)
        page_num += 1
    
    print(f"📄 Found {len(all_topics)} total topics across all pages")
    
    filtered_posts = []
    for topic in all_topics:
        created_at = parse_date(topic["created_at"])
        if DATE_FROM <= created_at <= DATE_TO:
            topic_url = f"{BASE_URL}/t/{topic['slug']}/{topic['id']}.json"
            
            try:
                response = session.get(topic_url, timeout=15)
                response.raise_for_status()
                topic_data = response.json()
            except requests.RequestException as e:
                print(f"⚠️ Error fetching topic {topic['id']}: {e}")
                continue
            
            posts = topic_data.get("post_stream", {}).get("posts", [])
            accepted_answer_id = topic_data.get("accepted_answer", topic_data.get("accepted_answer_post_id"))
            
            # Build reply count map
            reply_counter = {}
            for post in posts:
                reply_to = post.get("reply_to_post_number")
                if reply_to is not None:
                    reply_counter[reply_to] = reply_counter.get(reply_to, 0) + 1
            
            for post in posts:
                filtered_posts.append({
                    "topic_id": topic["id"],
                    "topic_title": topic.get("title"),
                    "category_id": topic.get("category_id"),
                    "tags": topic.get("tags", []),
                    "post_id": post["id"],
                    "post_number": post["post_number"],
                    "author": post["username"],
                    "created_at": post["created_at"],
                    "updated_at": post.get("updated_at"),
                    "reply_to_post_number": post.get("reply_to_post_number"),
                    "is_reply": post.get("reply_to_post_number") is not None,
                    "reply_count": reply_counter.get(post["post_number"], 0),
                    "like_count": post.get("like_count", 0),
                    "is_accepted_answer": post["id"] == accepted_answer_id,
                    "mentioned_users": [u["username"] for u in post.get("mentioned_users", [])],
                    "url": f"{BASE_URL}/t/{topic['slug']}/{topic['id']}/{post['post_number']}",
                    "content": BeautifulSoup(post["cooked"], "html.parser").get_text()
                })
    
    with open("discourse_posts.json", "w") as f:
        json.dump(filtered_posts, f, indent=2)
    
    print(f"✅ Scraped {len(filtered_posts)} posts between {DATE_FROM.date()} and {DATE_TO.date()}")


def main():
    # Check if cookies exist
    if not os.path.exists(COOKIES_FILE):
        # Check if storage state exists and extract cookies
        if os.path.exists(AUTH_STATE_FILE):
            print("📦 Found storage state, extracting cookies...")
            extract_cookies_from_storage_state()
        else:
            # Need to login
            with sync_playwright() as p:
                login_and_save_auth(p)
    
    # Verify cookies are still valid
    session = requests.Session()
    cookies = load_cookies_for_requests()
    session.cookies.update(cookies)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    if not is_authenticated_with_cookies(session):
        print("⚠️ Cookies invalid or expired. Re-authenticating...")
        with sync_playwright() as p:
            login_and_save_auth(p)
    else:
        print("✅ Using existing cookies")
    
    # Scrape using requests
    scrape_posts_with_requests()


if __name__ == "__main__":
    main()
