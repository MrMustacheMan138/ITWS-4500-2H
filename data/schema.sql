DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS programs CASCADE;
DROP TABLE IF EXISTS existingSources CASCADE;

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

-- Sources Info
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    source_identifier TEXT NOT NULL UNIQUE, -- URL or file path / hash
    source_type TEXT NOT NULL,              -- 'url' or 'pdf'
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);