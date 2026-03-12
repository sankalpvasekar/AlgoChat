import requests
import os
import time

repo_api = "https://api.github.com/repos/TheAlgorithms/Python/contents"
save_folder = "data/raw/github"

os.makedirs(save_folder, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0"}

# Allowed folders (DSA topics only)
allowed_topics = [
    "sorting",
    "searches",
    "graphs",
    "dynamic_programming",
    "linked_list",
    "stack",
    "queue",
    "recursion",
    "backtracking",
    "tree",
    "binary_tree",
]

def download_file(file_url, filename, folder):
    try:
        r = requests.get(file_url, headers=headers, timeout=10)

        if r.status_code == 200:
            path = os.path.join(folder, filename)

            with open(path, "w", encoding="utf-8") as f:
                f.write(r.text)

            print("Saved:", path)

    except Exception as e:
        print("Failed:", filename)


def scrape_github_folder(api_url, local_folder):

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        return

    items = response.json()

    for item in items:

        # Only enter allowed folders
        if item["type"] == "dir":

            if item["name"].lower() not in allowed_topics:
                continue

            new_folder = os.path.join(local_folder, item["name"])
            os.makedirs(new_folder, exist_ok=True)

            scrape_github_folder(item["url"], new_folder)

        elif item["type"] == "file":

            if item["name"].endswith(".py") or item["name"].endswith(".md"):

                download_file(item["download_url"], item["name"], local_folder)

                time.sleep(0.3)


scrape_github_folder(repo_api, save_folder)