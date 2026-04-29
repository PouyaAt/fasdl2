import requests
from bs4 import BeautifulSoup
import sys
import os

FASTDL_BASE = "https://fastdl.app/en"
POST_URL = os.getenv("IG_URL")

def write_error(msg):
    print(msg)
    with open("error_log.txt", "w", encoding="utf-8") as f:
        f.write(msg + "\n")

if not POST_URL:
    write_error("IG_URL environment variable is missing")
    sys.exit(1)

print("Downloading FastDL page for:", POST_URL)

# 1. Request FastDL page
try:
    r = requests.get(f"{FASTDL_BASE}/download?url={POST_URL}", timeout=20)
    r.raise_for_status()
except Exception as e:
    write_error("FASTDL REQUEST ERROR:\n" + repr(e))
    sys.exit(1)

html = r.text
with open("fastdl_output.html", "w", encoding="utf-8") as f:
    f.write(html)

print("FastDL page saved (fastdl_output.html). Length:", len(html))

# 2. Parse the FastDL page
soup = BeautifulSoup(html, "html.parser")

download_link = None
candidates = []

for a in soup.find_all("a"):
    href = a.get("href")
    if not href:
        continue
    if "instagram" in href or href.endswith(".jpg") or href.endswith(".mp4"):
        candidates.append(href)

if candidates:
    download_link = candidates[0]

# Save some debug info about found links
with open("found_links.txt", "w", encoding="utf-8") as f:
    f.write("Found candidate links:\n")
    for c in candidates:
        f.write(c + "\n")

if not download_link:
    write_error("ERROR: Could not locate download link in HTML.\nCheck found_links.txt")
    sys.exit(1)

print("Found media link:", download_link)

# 3. Download media
try:
    media = requests.get(download_link, timeout=20)
    media.raise_for_status()
except Exception as e:
    write_error("MEDIA DOWNLOAD ERROR:\n" + repr(e))
    sys.exit(1)

content_type = media.headers.get("Content-Type", "")
print("Content-Type:", content_type)

if "image" in content_type:
    ext = ".jpg"
elif "video" in content_type:
    ext = ".mp4"
else:
    ext = ""

filename = f"downloaded{ext}" if ext else "downloaded.bin"

print("Saving media as:", filename)

with open(filename, "wb") as f:
    f.write(media.content)

print("DONE. Saved:", filename)


https://www.instagram.com/p/C5_aFQxyz12/
