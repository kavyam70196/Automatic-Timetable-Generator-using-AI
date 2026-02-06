-- Fixed Database Setup for MIT Mysore Timetable System
-- Compatible with existing timetable-new.htm and enhanced.htm
-- Run in Supabase SQL Editor

-- =====================================================
-- 1. SUBJECTS TABLE (Enhanced with cross-department support)
-- =====================================================
CREATE TABLE IF NOT EXISTS subjects (
    id BIGSERIAL PRIMARY KEY,
    department VARCHAR(10) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 1 AND year <= 4),
    semester INTEGER NOT NULL CHECK (semester >= 1 AND semester <= 8),
    sub_code VARCHAR(20),
    name VARCHAR(100) NOT NULL,
    credits INTEGER NOT NULL DEFAULT 1 CHECK (credits >= 1 AND credits <= 6),
    type VARCHAR(20) NOT NULL DEFAULT 'theory' CHECK (type IN ('theory', 'lab', 'free')),
    weekly_hours INTEGER NOT NULL DEFAULT 3 CHECK (weekly_hours >= 1 AND weekly_hours <= 10),
    is_cross_dept BOOLEAN DEFAULT FALSE,
    teaching_dept VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add departments reference table
CREATE TABLE IF NOT EXISTS departments (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert standard departments
INSERT INTO departments (code, name) VALUES 
('CSE', 'Computer Science & Engineering'),
('ISE', 'Information Science & Engineering'),
('AIML', 'Artificial Intelligence & Machine Learning'),
('ECE', 'Electronics & Communication Engineering'),
('EEE', 'Electrical & Electronics Engineering'),
('MECH', 'Mechanical Engineering'),
('CIVIL', 'Civil Engineering'),
('AERO', 'Aerospace Engineering'),
('BIOTECH', 'Biotechnology'),
('CHEM', 'Chemical Engineering'),
('MATH', 'Mathematics'),
('PHYSICS', 'Physics'),
('CHEMISTRY', 'Chemistry'),
('LANG', 'Languages'),
('CONST', 'Constitution')
ON CONFLICT (code) DO NOTHING;

-- =====================================================
-- 2. FACULTY TABLE (Compatible with existing code)
-- =====================================================
CREATE TABLE IF NOT EXISTS faculty (
    id BIGSERIAL PRIMARY KEY,
    department VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    initials VARCHAR(20) NOT NULL,
    designation VARCHAR(50) NOT NULL DEFAULT 'assistant_professor' CHECK (designation IN (
        'professor', 'associate_professor', 'assistant_professor', 
        'lab_assistant', 'guest_faculty', 'visiting_faculty'
    )),
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. TIMETABLES TABLE (Enhanced for cross-department and conflict checking)
-- =====================================================
CREATE TABLE IF NOT EXISTS timetables (
    id BIGSERIAL PRIMARY KEY,
    faculty_name VARCHAR(100) NOT NULL,
    faculty_department VARCHAR(10) NOT NULL,
    subject_code VARCHAR(20) NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    day VARCHAR(20) NOT NULL CHECK (day IN ('Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
    time_slot INTEGER NOT NULL CHECK (time_slot >= 1 AND time_slot <= 6),
    section VARCHAR(10) NOT NULL,
    room VARCHAR(50),
    department VARCHAR(10) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    semester INTEGER NOT NULL CHECK (semester >= 1 AND semester <= 8),
    year INTEGER NOT NULL CHECK (year >= 1 AND year <= 4),
    type VARCHAR(20) DEFAULT 'theory' CHECK (type IN ('theory', 'lab', 'free')),
    is_cross_dept BOOLEAN DEFAULT FALSE,
    teaching_dept VARCHAR(50),
    is_finalized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(faculty_name, day, time_slot, academic_year)
);

-- =====================================================
-- 4. USERS TABLE (For login system)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    department VARCHAR(10) NOT NULL,
    recruiter_name VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 5. SECTIONS TABLE (For multiple sections)
-- =====================================================
CREATE TABLE IF NOT EXISTS sections (
    id BIGSERIAL PRIMARY KEY,
    department VARCHAR(10) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 1 AND year <= 4),
    semester INTEGER NOT NULL CHECK (semester >= 1 AND semester <= 8),
    section_name VARCHAR(10) NOT NULL,
    strength INTEGER DEFAULT 60 CHECK (strength >= 1 AND strength <= 120),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 6. FACULTY ASSIGNMENTS TABLE (Subject-Faculty mapping)
-- =====================================================
CREATE TABLE IF NOT EXISTS faculty_assignments (
    id BIGSERIAL PRIMARY KEY,
    subject_id BIGINT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    faculty_id BIGINT NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
    section VARCHAR(10) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 7. TIME SLOTS CONFIGURATION
-- =====================================================
CREATE TABLE IF NOT EXISTS time_slots (
    id BIGSERIAL PRIMARY KEY,
    department VARCHAR(10) NOT NULL,
    slot_name VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_type VARCHAR(20) NOT NULL CHECK (slot_type IN ('period', 'break', 'lunch')),
    period_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 8. INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_subjects_dept_year_sem ON subjects(department, academic_year, year, semester);
CREATE INDEX IF NOT EXISTS idx_subjects_type ON subjects(type);
CREATE INDEX IF NOT EXISTS idx_subjects_name ON subjects(name);

CREATE INDEX IF NOT EXISTS idx_faculty_dept ON faculty(department);
CREATE INDEX IF NOT EXISTS idx_faculty_initials ON faculty(initials);
CREATE INDEX IF NOT EXISTS idx_faculty_name ON faculty(name);

CREATE INDEX IF NOT EXISTS idx_timetables_dept_section ON timetables(department, section);
CREATE INDEX IF NOT EXISTS idx_timetables_faculty ON timetables(faculty_name);
CREATE INDEX IF NOT EXISTS idx_timetables_day_slot ON timetables(day, time_slot);

CREATE INDEX IF NOT EXISTS idx_users_dept ON users(department);

CREATE INDEX IF NOT EXISTS idx_assignments_subject ON faculty_assignments(subject_id);
CREATE INDEX IF NOT EXISTS idx_assignments_faculty ON faculty_assignments(faculty_id);

-- =====================================================
-- 9. UNIQUE CONSTRAINTS (Fixed syntax)
-- =====================================================
DO $$ 
BEGIN
    -- Add unique constraint for subjects if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_subject_per_semester' 
        AND table_name = 'subjects'
    ) THEN
        ALTER TABLE subjects ADD CONSTRAINT unique_subject_per_semester 
            UNIQUE (department, academic_year, year, semester, name);
    END IF;

    -- Add unique constraint for faculty if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_faculty_initials_per_dept' 
        AND table_name = 'faculty'
    ) THEN
        ALTER TABLE faculty ADD CONSTRAINT unique_faculty_initials_per_dept 
            UNIQUE (department, initials);
    END IF;

    -- Add unique constraint for users if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_user_per_dept' 
        AND table_name = 'users'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT unique_user_per_dept 
            UNIQUE (department);
    END IF;

    -- Add unique constraint for sections if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_section_per_semester' 
        AND table_name = 'sections'
    ) THEN
        ALTER TABLE sections ADD CONSTRAINT unique_section_per_semester 
            UNIQUE (department, academic_year, year, semester, section_name);
    END IF;

    -- Add unique constraint for faculty assignments if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_faculty_assignment' 
        AND table_name = 'faculty_assignments'
    ) THEN
        ALTER TABLE faculty_assignments ADD CONSTRAINT unique_faculty_assignment 
            UNIQUE (subject_id, faculty_id, section, academic_year);
    END IF;
END $$;

-- =====================================================
-- 10. ROW LEVEL SECURITY (RLS)
-- =====================================================
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE faculty ENABLE ROW LEVEL SECURITY;
ALTER TABLE timetables ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE faculty_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_slots ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- 11. RLS POLICIES (Allow all for now)
-- =====================================================
DROP POLICY IF EXISTS "Allow all operations on subjects" ON subjects;
CREATE POLICY "Allow all operations on subjects" ON subjects FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow all operations on faculty" ON faculty;
CREATE POLICY "Allow all operations on faculty" ON faculty FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow all operations on timetables" ON timetables;
CREATE POLICY "Allow all operations on timetables" ON timetables FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow all operations on users" ON users;
CREATE POLICY "Allow all operations on users" ON users FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow all operations on sections" ON sections;
CREATE POLICY "Allow all operations on sections" ON sections FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow all operations on faculty_assignments" ON faculty_assignments;
CREATE POLICY "Allow all operations on faculty_assignments" ON faculty_assignments FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow all operations on time_slots" ON time_slots;
CREATE POLICY "Allow all operations on time_slots" ON time_slots FOR ALL USING (true);

-- =====================================================
-- 12. FUNCTIONS AND TRIGGERS
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_subjects_updated_at ON subjects;
CREATE TRIGGER update_subjects_updated_at BEFORE UPDATE ON subjects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_faculty_updated_at ON faculty;
CREATE TRIGGER update_faculty_updated_at BEFORE UPDATE ON faculty
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 13. COMPLETION MESSAGE
-- =====================================================
SELECT 
    '✅ Database Setup Complete!' as status,
    'All tables, indexes, and constraints created successfully.' as message,
    NOW() as completed_at;