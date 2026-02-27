import requests
from bs4 import BeautifulSoup
import psycopg2
import re
import csv
import time
from config import DB_CONFIG

# Connect to PostgreSQL
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

def insert_program(name):
    cursor.execute(
        # Send program info to database
        "INSERT INTO programs (program_name, degree, level_id) VALUES (%s, %s, 1) RETURNING id",
        (name, "B.S.")
    )
    return cursor.fetchone()[0]

def insert_year(program_id, year_name):
    cursor.execute(
        # Send program year info to database
        "INSERT INTO program_years (program_id, year_name) VALUES (%s, %s) RETURNING id",
        (program_id, year_name)
    )
    return cursor.fetchone()[0]

def insert_semester(year_id, semester_name, credits):
    cursor.execute(
        # Send semester info to database
        "INSERT INTO semesters (year_id, semester_name, total_credits) VALUES (%s, %s, %s) RETURNING id",
        (year_id, semester_name, credits)
    )
    return cursor.fetchone()[0]

def insert_course(semester_id, code, title, credits):
    cursor.execute(
        # Send course info to database
        "INSERT INTO courses (semester_id, course_code, course_title, credit_hours) VALUES (%s, %s, %s, %s)",
        (semester_id, code, title, credits)
    )

# Match the academic year headings
year_pattern = re.compile(r'(First Year|Second Year|Third Year|Fourth Year)')

# Match the semester lines like: Fall Semester (17 credits)
semester_pattern = re.compile(r'(Fall Semester|Spring Semester).*?\((\d+) credits\)')

# Match the course lines
course_pattern = re.compile(r'([A-Z]{2,5}\s?\d{4})\s*-\s*(.*?)\s*Credit Hours:\s*(\d+)')

with open("program_links.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        name = row["program_name"]
        url = row["url"]

        print(f"Processing {name}")

        # Insert program info
        program_id = insert_program(name)

        # Download the program page
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract all visible text
        text = soup.get_text("\n")

        # Split the text into academic year sections
        years = year_pattern.split(text)

        # Loop through the detected years
        for i in range(1, len(years), 2):
            year_name = years[i]
            year_content = years[i+1]

            year_id = insert_year(program_id, year_name)

            # Find the semesters inside year
            semesters = semester_pattern.findall(year_content)

            for sem_name, credits in semesters:
                semester_id = insert_semester(year_id, sem_name, int(credits))

                # Extract the courses inside the semester block
                for code, title, ch in course_pattern.findall(year_content):
                    insert_course(semester_id, code, title, int(ch))

        # Commit after each program
        conn.commit()

        # Slight delay to avoid overwhelming server
        time.sleep(1)

cursor.close()
conn.close()

print("Scraping complete.")