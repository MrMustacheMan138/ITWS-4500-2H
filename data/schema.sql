DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS semesters CASCADE;
DROP TABLE IF EXISTS program_years CASCADE;
DROP TABLE IF EXISTS programs CASCADE;
DROP TABLE IF EXISTS program_levels CASCADE;

-- Program Level (Bachelors, Masters, etc.)
CREATE TABLE IF NOT EXISTS program_levels (
    id SERIAL PRIMARY KEY,
    level_name TEXT UNIQUE NOT NULL
);

-- Program Info
CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
    program_name TEXT NOT NULL,
    degree TEXT,
    level_id INT REFERENCES program_levels(id)
);

-- Year 
CREATE TABLE IF NOT EXISTS program_years (
    id SERIAL PRIMARY KEY,
    program_id INT REFERENCES programs(id) ON DELETE CASCADE,
    year_name TEXT
);

-- Semester 
CREATE TABLE IF NOT EXISTS semesters (
    id SERIAL PRIMARY KEY,
    year_id INT REFERENCES program_years(id) ON DELETE CASCADE,
    semester_name TEXT,
    total_credits INT
);

-- Courses
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    semester_id INT REFERENCES semesters(id) ON DELETE CASCADE,
    course_code TEXT,
    course_title TEXT,
    credit_hours INT
);

INSERT INTO program_levels (level_name)
VALUES ('Baccalaureate');