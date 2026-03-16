import requests
from bs4 import BeautifulSoup
import psycopg2
import re
import time
from config import DB_CONFIG

BASE = "https://catalog.rpi.edu/"
PROGRAM_PAGE = "https://catalog.rpi.edu/content.php?catoid=24&navoid=604"

# connect to database
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# insert program into programs table
def insert_program(name):
    cursor.execute(
        """
        INSERT INTO programs (program_name, degree, level)
        VALUES (%s,%s,%s)
        """,
        (name, "B.S.", "Baccalaureate")
    )

# insert course into courses table
def insert_course(program, code, title, credits):
    cursor.execute(
        """
        INSERT INTO courses
        (program_name, course_code, course_title, credit_hours)
        VALUES (%s,%s,%s,%s)
        """,
        (program, code, title, credits)
    )

print("Downloading program list...")

# download program page
r = requests.get(PROGRAM_PAGE)
soup = BeautifulSoup(r.text, "html.parser")

program_links = []

# extract program links
for a in soup.find_all("a"):

    href = a.get("href")
    text = a.get_text(strip=True)

    if href and "preview_program.php" in href:
        program_links.append((text, BASE + href))

print(f"{len(program_links)} programs found")

# regex to get courses
course_pattern = re.compile(
    r'([A-Z]{2,5}\s?\d{4})\s*-\s*(.*?)\s*Credit Hours:\s*(\d+)'
)

# loop through each program
for program_name, program_url in program_links:

    print("Processing:", program_name)

    insert_program(program_name)

    r = requests.get(program_url)
    soup = BeautifulSoup(r.text, "html.parser")

    # get full page text info
    text = soup.get_text("\n")

    matches = course_pattern.findall(text)

    for code, title, credits in matches:

        insert_course(
            program_name,
            code.strip(),
            title.strip(),
            int(credits)
        )

    conn.commit()

    # slight delay
    time.sleep(1)

cursor.close()
conn.close()

print("Scraping complete.")