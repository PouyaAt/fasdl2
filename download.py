import os
import traceback
from instaloader import Instaloader, Profile

DEBUG_LOG = "debug_log.txt"
ERROR_LOG = "error_log.txt"

def log(message):
    print(message)
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(message + "\n")

try:
    username = os.getenv("IG_USERNAME")
    if not username:
        raise Exception("IG_USERNAME environment variable is missing")

    username = username.strip()
    log(f"Target username: {username}")

    L = Instaloader(
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        download_video_thumbnails=False
    )

    profile = Profile.from_username(L.context, username)

    # --------------------------
    # Download profile picture
    # --------------------------
    log("Downloading profile picture...")
    L.download_pic("profile_pic", profile.profile_pic_url, profile.profile_pic_url)
    os.rename("profile_pic.jpg", "profile_pic.jpg")
    log("Saved profile_pic.jpg")

    # --------------------------
    # Download recent post thumbnails
    # --------------------------
    log("Collecting posts...")
    posts = list(profile.get_posts())[:5]
    log(f"Found {len(posts)} posts to download")

    count = 1
    for post in posts:
        thumb_url = post.url  # thumbnail or main image
        log(f"Downloading post {count}: {thumb_url}")
        L.download_pic(f"post_{count}", thumb_url, thumb_url)
        os.rename(f"post_{count}.jpg", f"post_{count}.jpg")
        log(f"Saved post_{count}.jpg")
        count += 1

    log("All downloads completed successfully.")

except Exception as e:
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        f.write(str(e) + "\n")
        f.write(traceback.format_exc())
    print("ERROR — check error_log.txt")
