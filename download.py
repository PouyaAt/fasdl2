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
    username = os.getenv("IG_USERNAME")
    if not username:
        raise Exception("IG_USERNAME environment variable is missing")

    log(f"Username received: {username}")
    api_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    log(f"Requesting Instagram JSON from: {api_url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    resp = requests.get(
    api_url,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Referer": f"https://www.instagram.com/{username}/"
    },
    allow_redirects=True
)

    log(f"Instagram response status: {resp.status_code}")

    if resp.status_code not in (200, 302):
        raise Exception(f"Instagram returned {resp.status_code}")

    data = resp.json()

    # Determine user data (account structure slightly differs sometimes)
    user = data.get("graphql", {}).get("user")
    if not user:
        user = data.get("data", {}).get("user")
    if not user:
        raise Exception("Could not locate 'user' object in JSON")

    # --- Profile picture ---
    profile_url = user.get("profile_pic_url_hd") or user.get("profile_pic_url")
    if not profile_url:
        raise Exception("Profile picture URL not found in JSON")

    log(f"Downloading profile picture: {profile_url}")
    img_resp = requests.get(profile_url, headers=headers)
    if img_resp.status_code == 200:
        with open("profile_pic.jpg", "wb") as f:
            f.write(img_resp.content)
        log("Profile picture saved as profile_pic.jpg")
    else:
        raise Exception(f"Profile picture download failed: {img_resp.status_code}")

    # --- Recent post thumbnails ---
    posts = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
    log(f"Found {len(posts)} posts.")

    for i, post in enumerate(posts[:5], start=1):  # download first 5
        thumb = post.get("node", {}).get("thumbnail_src")
        if thumb:
            log(f"Downloading thumbnail {i}: {thumb}")
            r = requests.get(thumb, headers=headers)
            if r.status_code == 200:
                fname = f"post_{i}.jpg"
                with open(fname, "wb") as f:
                    f.write(r.content)
                log(f"Saved {fname}")
            else:
                log(f"Failed thumbnail {i} ({r.status_code})")
        else:
            log(f"No thumbnail found for post {i}")

    log("All downloads complete.")

except Exception as e:
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        f.write(str(e) + "\n\n")
        f.write(traceback.format_exc())
    print("ERROR OCCURRED — see error_log.txt")
