import requests
import os
import re
import traceback

DEBUG_LOG = "debug_log.txt"
ERROR_LOG = "error_log.txt"

def log(msg):
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

try:
    username = os.getenv("IG_USERNAME")

    if not username:
        raise Exception("IG_USERNAME environment variable is missing")

    log(f"Username received: {username}")

    fastdl_url = f"https://fastdl.app/en/{username}"
    log(f"Requesting FastDL page: {fastdl_url}")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(fastdl_url, headers=headers)

    log(f"FastDL response status: {resp.status_code}")

    html = resp.text

    with open("fastdl_profile_output.html", "w", encoding="utf-8") as f:
        f.write(html)

    log("Saved FastDL HTML to fastdl_profile_output.html")

    # Try to locate instagram CDN image
    match = re.search(r'(https://[^"]*cdninstagram[^"]+\.jpg)', html)

    if not match:
        raise Exception("Could not locate profile picture URL in FastDL HTML")

    img_url = match.group(1)

    log(f"Profile picture URL found: {img_url}")

    img_resp = requests.get(img_url, headers=headers)

    log(f"Image download status: {img_resp.status_code}")

    if img_resp.status_code != 200:
        raise Exception(f"Image request failed with {img_resp.status_code}")

    with open("profile_pic.jpg", "wb") as f:
        f.write(img_resp.content)

    log("Profile picture saved as profile_pic.jpg")

except Exception as e:
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        f.write(str(e) + "\n\n")
        f.write(traceback.format_exc())

    print("ERROR OCCURRED — see error_log.txt")
