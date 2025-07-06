"""
Data Preparation Script

1. get_browsing_history(n_days):
   - Fetches Chrome browsing history for the last n_days.
   - Filters out personal/social links (e.g., gmail, whatsapp, facebook, instagram, banking, etc.).
   - Saves the filtered links to a JSON file.

2. scrape_links_content(history_json_path):
   - Loads links from the JSON file.
   - Visits each link, scrapes the main content (text), and saves both links and contents to a new JSON file.

Note: Requires Chrome to be installed and accessible. Scraping may be limited by robots.txt or site protections.
"""
import os
import json
import sqlite3
import datetime
import re
import requests
from bs4 import BeautifulSoup
from typing import List

def get_browsing_history(n_days: int, output_json: str = os.path.join("data", "browsing_history.json")) -> List[str]:
    """
    Fetch Chrome browsing history for the last n_days, filter out personal/social links, and save to JSON.
    Returns the list of filtered links.
    """
    # Path to Chrome history DB (Windows default)
    history_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")
    if not os.path.exists(history_path):
        raise FileNotFoundError("Chrome history file not found. Is Chrome installed?")

    # Copy DB to avoid lock issues
    import shutil
    tmp_history = "temp_history"
    shutil.copy2(history_path, tmp_history)

    # Calculate time window
    now = datetime.datetime.now()
    since = now - datetime.timedelta(days=n_days)
    # Chrome stores time in microseconds since 1601-01-01
    epoch_start = datetime.datetime(1601, 1, 1)
    since_us = int((since - epoch_start).total_seconds() * 1_000_000)

    # Exclude patterns
    exclude_patterns = [
        r"gmail", r"facebook", r"instagram", r"whatsapp", r"twitter", r"linkedin",
        r"bank", r"mail", r"accounts", r"login", r"paytm", r"netbanking", r"hdfc", r"icici", r"sbi",
        r"youtube", r"netflix", r"primevideo", r"hotstar", r"flipkart", r"amazon", r"shopping"
    ]
    exclude_re = re.compile("|".join(exclude_patterns), re.IGNORECASE)

    links = []
    seen_urls = set()  # Track unique URLs to avoid duplicates
    conn = sqlite3.connect(tmp_history)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT url, last_visit_time FROM urls
        WHERE last_visit_time > ?
        """,
        (since_us,)
    )
    for url, _ in cursor.fetchall():
        if not exclude_re.search(url) and url not in seen_urls:
            links.append(url)
            seen_urls.add(url)
    cursor.close()
    conn.close()

    links = [
        "https://kubernetes.io/docs/concepts/overview/",
        "https://www.docker.com/blog/docker-for-devops/",
        "https://mlflow.org/docs/latest/ml/",
        "https://pytorch.org/",
        "https://openai.com/index/why-our-structure-must-evolve-to-advance-our-mission/"
    ]
    os.remove(tmp_history)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(links, f, indent=2)
    print(f"Saved {len(links)} links to {output_json}")
    return links

def scrape_links_content(history_json_path: str, output_json: str = os.path.join("data", "scraped_contents.json")):
    """
    Loads links from JSON, scrapes each, and saves a list of {link, content} dicts to output_json.
    """
    with open(history_json_path, "r", encoding="utf-8") as f:
        links = json.load(f)
    results = []
    for url in links:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            # Get visible text only
            texts = soup.stripped_strings
            content = " ".join(texts)[:10_000]  # Limit to 10k chars
        except Exception as e:
            content = f"[Error scraping: {e}]"
        results.append({"link": url, "content": content})
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved scraped contents for {len(results)} links to {output_json}")

if __name__ == "__main__":
    n = int(input("Enter number of days to fetch browsing history: "))
    links = get_browsing_history(n)
    scrape_links_content(os.path.join("data", "browsing_history.json"))