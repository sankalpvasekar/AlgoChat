import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
import time

url = "https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

links = []

# Extract links
for a in soup.find_all("a", href=True):
    link = a['href']

    if "geeksforgeeks.org" in link:
        links.append(link)

# Remove duplicates
links = list(set(links))

print("Total links found:", len(links))


# -------- FILTER LINKS --------
filtered_links = [
    link for link in links
    if link.startswith("https://www.geeksforgeeks.org/")
    and "dsa" in link
    and "courses" not in link
    and "quiz" not in link
    and "quizzes" not in link
    and "privacy" not in link
    and "contact" not in link
    and "legal" not in link
    and "facebook" not in link
    and "connect" not in link
    and "category" not in link
]

# Select first 30 good links
links_to_scrape = filtered_links[:30]

print("Links selected for scraping:", len(links_to_scrape))


# -------- CREATE FOLDER --------
save_folder = "data/raw/geeksforgeeks"
os.makedirs(save_folder, exist_ok=True)


# -------- FUNCTION FOR SAFE FILENAME --------
def get_filename(url):
    path = urlparse(url).path.strip("/")
    if not path:
        return "homepage.txt"
    return path.replace("/", "_") + ".txt"


# -------- SCRAPE EACH PAGE --------
for link in links_to_scrape:

    try:
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")

        text = soup.get_text()

        filename = get_filename(link)

        with open(f"{save_folder}/{filename}", "w", encoding="utf-8") as f:
            f.write(text)

        print("Saved:", filename)

    except Exception as e:
        print("Failed:", link)




save_folder = "mit_courses"
os.makedirs(save_folder, exist_ok=True)


def get_filename(url):
    return url.strip("/").split("/")[-1] + ".txt"


headers = {
    "User-Agent": "Mozilla/5.0"
}


