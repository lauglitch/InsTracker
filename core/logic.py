import json, zipfile, io, re
from urllib.parse import urlparse

FOLLOWERS_REGEX = re.compile(r"followers(_\d+)?\.json$", re.IGNORECASE)
FOLLOWING_REGEX = re.compile(r"following(_\d+)?\.json$", re.IGNORECASE)


def normalize(username):
    return username.strip().lower() if username else None


def extract_username(entry):
    try:
        for item in entry.get("string_list_data", []):
            val = item.get("value")
            if val:
                return normalize(val)
    except:
        pass

    if entry.get("title"):
        return normalize(entry["title"])

    try:
        for item in entry.get("string_list_data", []):
            href = item.get("href", "")
            if href:
                path = urlparse(href).path.strip("/")
                if path.startswith("_u/"):
                    path = path[3:]
                return normalize(path.split("/")[0])
    except:
        pass

    return None


def find_json_files(names):
    followers = [n for n in names if FOLLOWERS_REGEX.search(n)]
    following = [n for n in names if FOLLOWING_REGEX.search(n)]
    return sorted(followers), sorted(following)


def load_data(zip_bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as z:
        names = z.namelist()
        follower_files, following_files = find_json_files(names)

        followers_entries = []
        for f in follower_files:
            data = json.loads(z.read(f).decode("utf-8"))

            if isinstance(data, list):
                followers_entries.extend(data)

            elif isinstance(data, dict) and "relationships_followers" in data:
                followers_entries.extend(data["relationships_followers"])

        following_entries = []
        for f in following_files:
            data = json.loads(z.read(f).decode("utf-8"))

            if isinstance(data, dict) and "relationships_following" in data:
                following_entries.extend(data["relationships_following"])

            elif isinstance(data, list):
                following_entries.extend(data)

        followers = set(filter(None, (extract_username(e) for e in followers_entries)))
        following = set(filter(None, (extract_username(e) for e in following_entries)))

        return followers, following
