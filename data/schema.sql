DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS programs CASCADE;

-- Program Info
CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    program_name TEXT NOT NULL,
    degree TEXT,
    level TEXT
);

-- Course Info
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    program_name TEXT NOT NULL,
    course_code TEXT,
    course_title TEXT,
    credit_hours INT
);