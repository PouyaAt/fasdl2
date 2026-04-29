import requests, re, sys, os

username = os.getenv("IG_USERNAME")
if not username:
    print("ERROR: IG_USERNAME environment variable is missing")
    sys.exit(1)

fastdl_url = f"https://fastdl.app/en/{username}"
print(f"Fetching: {fastdl_url}")

headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(fastdl_url, headers=headers)

if resp.status_code != 200:
    print(f"ERROR: FastDL responded with {resp.status_code}")
    sys.exit(1)

html = resp.text

# Save HTML for debugging
with open("fastdl_output.html", "w", encoding="utf-8") as f:
    f.write(html)

# Regex to extract profile picture from FastDL page
match = re.search(r'src="(https://[^"]+instagram[^"]+\.jpg)"', html)

if not match:
    print("ERROR: Could not locate profile picture URL in FastDL HTML")
    sys.exit(1)

profile_pic_url = match.group(1)
print("FOUND PROFILE PIC URL:", profile_pic_url)

# Download profile picture
pic_resp = requests.get(profile_pic_url, headers=headers)

if pic_resp.status_code != 200:
    print(f"ERROR: Failed to download image: {pic_resp.status_code}")
    sys.exit(1)

with open("profile_pic.jpg", "wb") as f:
    f.write(pic_resp.content)

print("SUCCESS: profile_pic.jpg downloaded")
