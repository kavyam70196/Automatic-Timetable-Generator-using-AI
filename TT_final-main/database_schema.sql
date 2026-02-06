-- Complete Database Schema for MIT Mysore Timetable System
-- Drop existing tables if needed
DROP TABLE IF EXISTS timetables CASCADE;
DROP TABLE IF EXISTS faculty_assignments CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS faculty CASCADE;
DROP TABLE IF EXISTS sections CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table (Department-wise authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    recruiter_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(department)
);

-- Faculty table
CREATE TABLE faculty (
    id SERIAL PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    initials VARCHAR(10) NOT NULL,
    email VARCHAR(255),
    designation VARCHAR(100),
    phone VARCHAR(20),
    specialization VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(department, name)
);

-- Subjects table with sub_code
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 4),
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    sub_code VARCHAR(20),
    name VARCHAR(255) NOT NULL,
    credits INTEGER DEFAULT 3 CHECK (credits BETWEEN 1 AND 6),
    type VARCHAR(20) DEFAULT 'theory' CHECK (type IN ('theory', 'lab', 'mcq', 'free')),
    weekly_hours INTEGER DEFAULT 3 CHECK (weekly_hours BETWEEN 1 AND 10),
    is_cross_dept BOOLEAN DEFAULT FALSE,
    teaching_dept VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(department, academic_year, year, semester, name)
);

-- Sections table
CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    section_name VARCHAR(10) NOT NULL,
    room_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(department, academic_year, year, semester, section_name)
);

-- Faculty assignments (Subject-Faculty mapping)
CREATE TABLE faculty_assignments (
    id SERIAL PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    section_name VARCHAR(10) NOT NULL,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(department, academic_year, year, semester, section_name, subject_id)
);

-- Timetables table (Generated timetables)
CREATE TABLE timetables (
    id SERIAL PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    section VARCHAR(10) NOT NULL,
    day VARCHAR(20) NOT NULL CHECK (day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')),
    time_slot INTEGER NOT NULL CHECK (time_slot BETWEEN 1 AND 6),
    subject_code VARCHAR(20),
    subject_name VARCHAR(255) NOT NULL,
    faculty_name VARCHAR(255),
    room VARCHAR(50),
    periods INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(department, academic_year, year, semester, section, day, time_slot)
);

-- Indexes for performance
CREATE INDEX idx_subjects_dept ON subjects(department, academic_year, year, semester);
CREATE INDEX idx_faculty_dept ON faculty(department);
CREATE INDEX idx_timetables_lookup ON timetables(department, academic_year, year, semester, section);
CREATE INDEX idx_timetables_faculty ON timetables(faculty_name, day, time_slot);
CREATE INDEX idx_faculty_assignments ON faculty_assignments(department, academic_year, year, semester, section_name);

-- Sample data for testing
INSERT INTO users (department, password, recruiter_name) VALUES
('ISE', 'ise123', 'Dr. ISE Head'),
('CSE', 'cse123', 'Dr. CSE Head'),
('AIML', 'aiml123', 'Dr. AIML Head');

INSERT INTO faculty (department, name, initials, email) VALUES
('ISE', 'Dr. Rajesh Kumar', 'RK', 'rajesh@mit.ac.in'),
('ISE', 'Prof. Priya Sharma', 'PS', 'priya@mit.ac.in'),
('ISE', 'Dr. Amit Patel', 'AP', 'amit@mit.ac.in'),
('ISE', 'Prof. Sneha Reddy', 'SR', 'sneha@mit.ac.in'),
('ISE', 'Dr. Vikram Singh', 'VS', 'vikram@mit.ac.in');

-- Sample subjects with sub_code
INSERT INTO subjects (department, academic_year, year, semester, sub_code, name, credits, type, weekly_hours) VALUES
('ISE', '2024-25', 3, 5, 'IS501', 'Theory of Computation', 4, 'theory', 4),
('ISE', '2024-25', 3, 5, 'IS502', 'Computer Networks & Security', 4, 'theory', 4),
('ISE', '2024-25', 3, 5, 'IS503', 'Software Testing', 3, 'theory', 3),
('ISE', '2024-25', 3, 5, 'IS504', 'Data Mining & Data Warehousing', 3, 'theory', 3),
('ISE', '2024-25', 3, 5, 'IS505', 'Machine Learning', 3, 'theory', 3),
('ISE', '2024-25', 3, 5, 'IS506L', 'ML Lab', 2, 'lab', 2),
('ISE', '2024-25', 3, 5, 'IS507L', 'CNS Lab', 2, 'lab', 2);

COMMENT ON TABLE subjects IS 'Stores all subjects with sub_code for timetable display';
COMMENT ON TABLE timetables IS 'Generated timetables with clash-free scheduling';
COMMENT ON TABLE faculty IS 'Faculty database for all departments';
COMMENT ON TABLE faculty_assignments IS 'Maps subjects to faculty for each section';
