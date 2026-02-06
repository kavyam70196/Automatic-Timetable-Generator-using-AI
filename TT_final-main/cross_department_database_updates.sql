-- Cross-Department Database Updates
-- Run ONLY if you need to add cross-department support to existing tables
-- Skip if tables already have these columns

-- Add cross-department columns to subjects table
DO $$ 
BEGIN
    -- Add is_cross_dept column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subjects' 
        AND column_name = 'is_cross_dept'
    ) THEN
        ALTER TABLE subjects ADD COLUMN is_cross_dept BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Add teaching_dept column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subjects' 
        AND column_name = 'teaching_dept'
    ) THEN
        ALTER TABLE subjects ADD COLUMN teaching_dept VARCHAR(50);
    END IF;
END $$;

-- Add cross-department columns to timetables table
DO $$ 
BEGIN
    -- Add faculty_department column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'timetables' 
        AND column_name = 'faculty_department'
    ) THEN
        ALTER TABLE timetables ADD COLUMN faculty_department VARCHAR(10);
    END IF;
    
    -- Add is_cross_dept column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'timetables' 
        AND column_name = 'is_cross_dept'
    ) THEN
        ALTER TABLE timetables ADD COLUMN is_cross_dept BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Add teaching_dept column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'timetables' 
        AND column_name = 'teaching_dept'
    ) THEN
        ALTER TABLE timetables ADD COLUMN teaching_dept VARCHAR(50);
    END IF;
END $$;

-- Create departments table if it doesn't exist
CREATE TABLE IF NOT EXISTS departments (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert standard departments (only if table is empty)
INSERT INTO departments (code, name) 
SELECT * FROM (VALUES 
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
) AS v(code, name)
WHERE NOT EXISTS (SELECT 1 FROM departments WHERE departments.code = v.code);

-- Add unique constraint for faculty conflicts (only if it doesn't exist)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_faculty_schedule' 
        AND table_name = 'timetables'
    ) THEN
        ALTER TABLE timetables ADD CONSTRAINT unique_faculty_schedule 
            UNIQUE(faculty_name, day, time_slot, academic_year);
    END IF;
END $$;

-- Enable RLS on new table
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;

-- Add RLS policy for departments
DROP POLICY IF EXISTS "Allow all operations on departments" ON departments;
CREATE POLICY "Allow all operations on departments" ON departments FOR ALL USING (true);

-- Verification query
SELECT 
    'Cross-Department Setup Complete' as status,
    (SELECT COUNT(*) FROM departments) as departments_count,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'subjects' AND column_name = 'is_cross_dept') as subjects_updated,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'timetables' AND column_name = 'faculty_department') as timetables_updated;