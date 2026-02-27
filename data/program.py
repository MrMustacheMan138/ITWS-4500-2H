import requests
from bs4 import BeautifulSoup
import csv

# Base URL 
BASE = "https://catalog.rpi.edu/"

# Main programs page
PROGRAM_PAGE = "https://catalog.rpi.edu/content.php?catoid=33&navoid=873"

# Download page info
response = requests.get(PROGRAM_PAGE)
soup = BeautifulSoup(response.text, "html.parser")

links = []

# Find all anchor tags
for a in soup.find_all("a"):
    href = a.get("href")
    text = a.get_text(strip=True)

    # Program links contain preview_program.php
    if href and "preview_program.php" in href:
        full_url = BASE + href
        links.append([text, full_url])

# Save links to the CSV
with open("program_links.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["program_name", "url"])
    writer.writerows(links)

print(f"Saved {len(links)} program links.")