import os
import requests
from bs4 import BeautifulSoup

DEBUG_LOG = "debug_log.txt"
ERROR_LOG = "error_log.txt"

def log(msg):
    print(msg)
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

try:
    username = os.getenv("IG_USERNAME")
    if not username:
        raise Exception("IG_USERNAME environment variable missing")

    username = username.strip()
    log(f"Target username: {username}")

    # Public Instagram viewer that works in GitHub Actions
    url = f"https://imginn.com/{username}/"
    log(f"Requesting page: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)

    log(f"Response status: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"Failed to fetch profile page ({response.status_code})")

    soup = BeautifulSoup(response.text, "html.parser")

    # Profile picture is inside meta property og:image
    meta = soup.find("meta", property="og:image")
    if not meta:
        raise Exception("Could not find profile picture meta tag")

    profile_pic_url = meta["content"]
    log(f"Profile picture URL found: {profile_pic_url}")

    # Download image
    img_data = requests.get(profile_pic_url, headers=headers, timeout=15).content

    with open("profile_pic.jpg", "wb") as f:
        f.write(img_data)

    log("Saved profile_pic.jpg successfully ✅")

except Exception as e:
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        f.write(str(e))
    print("ERROR — check error_log.txt")
