import os
import requests
import traceback

DEBUG_LOG = "debug_log.txt"
ERROR_LOG = "error_log.txt"

def log(msg):
    print(msg)
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

try:
    # ----------------------------------------------------
    # 1. Read username
    # ----------------------------------------------------
    username = os.getenv("IG_USERNAME")
    if not username:
        raise Exception("IG_USERNAME environment variable is missing")

    username = username.strip()
    log(f"Username received: {username}")

    # ----------------------------------------------------
    # 2. Instagram public API endpoint
    # ----------------------------------------------------
    api_url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    log(f"Requesting Instagram JSON from: {api_url}")

    headers = {
        "User-Agent": "Instagram 155.0.0.37.107",  # mobile-style UA
        "x-ig-app-id": "936619743392459",          # required app ID
        "Accept": "application/json"
    }

    resp = requests.get(api_url, headers=headers)
    log(f"Instagram response status: {resp.status_code}")

    if resp.status_code != 200:
        raise Exception(f"Instagram returned {resp.status_code}")

    # ----------------------------------------------------
    # 3. Parse JSON
    # ----------------------------------------------------
    data = resp.json()

    if "data" not in data or "user" not in data["data"]:
        raise Exception("Invalid API response: no 'data.user' object")

    user = data["data"]["user"]

    # ----------------------------------------------------
    # 4. Download profile picture
    # ----------------------------------------------------
    profile_url = user.get("profile_pic_url_hd") or user.get("profile_pic_url")
    if not profile_url:
        raise Exception("Profile picture URL not found in JSON")

    log(f"Downloading profile picture: {profile_url}")
    r = requests.get(profile_url, headers=headers)

    if r.status_code == 200:
        with open("profile_pic.jpg", "wb") as f:
            f.write(r.content)
        log("Saved profile_pic.jpg")
    else:
        raise Exception(f"Profile picture download failed: {r.status_code}")

    # ----------------------------------------------------
    # 5. Download 5 recent post thumbnails
    # ----------------------------------------------------
    posts = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
    log(f"Found {len(posts)} posts total.")

    max_posts = min(5, len(posts))

    for i in range(max_posts):
        node = posts[i].get("node", {})
        thumb_url = node.get("thumbnail_src")

        if not thumb_url:
            log(f"No thumbnail for post {i+1}, skipping")
            continue

        log(f"Downloading post {i+1}: {thumb_url}")
        rr = requests.get(thumb_url, headers=headers)

        if rr.status_code == 200:
            fname = f"post_{i+1}.jpg"
            with open(fname, "wb") as f:
                f.write(rr.content)
            log(f"Saved {fname}")
        else:
            log(f"Failed thumbnail {i+1}: {rr.status_code}")

    log("All downloads completed successfully.")

except Exception as e:
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        f.write(str(e) + "\n")
        f.write(traceback.format_exc())
    print("ERROR OCCURRED — see error_log.txt")
