-- Database Updates for MIT Mysore Timetable System
-- Run these commands in Supabase SQL Editor to fix existing tables
-- Only run if you have existing tables that need updates

-- =====================================================
-- 1. UPDATE TIMETABLES TABLE STRUCTURE
-- =====================================================

-- Remove default values and make fields required
ALTER TABLE timetables 
ALTER COLUMN academic_year DROP DEFAULT,
ALTER COLUMN academic_year SET NOT NULL;

ALTER TABLE timetables 
ALTER COLUMN year DROP DEFAULT,
ALTER COLUMN year SET NOT NULL;

ALTER TABLE timetables 
ALTER COLUMN semester DROP DEFAULT,
ALTER COLUMN semester SET NOT NULL;

-- Add constraints if they don't exist
DO $$ 
BEGIN
    -- Add year constraint
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'timetables_year_check'
    ) THEN
        ALTER TABLE timetables ADD CONSTRAINT timetables_year_check 
            CHECK (year >= 1 AND year <= 4);
    END IF;

    -- Add semester constraint  
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'timetables_semester_check'
    ) THEN
        ALTER TABLE timetables ADD CONSTRAINT timetables_semester_check 
            CHECK (semester >= 1 AND semester <= 8);
    END IF;
END $$;

-- =====================================================
-- 2. ADD MISSING INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_timetables_year_sem ON timetables(year, semester);
CREATE INDEX IF NOT EXISTS idx_timetables_academic_year ON timetables(academic_year);
CREATE INDEX IF NOT EXISTS idx_timetables_full_key ON timetables(department, academic_year, year, semester, section);

-- =====================================================
-- 3. CLEAN UP ANY INVALID DATA
-- =====================================================

-- Remove any entries with invalid years or semesters
DELETE FROM timetables WHERE year < 1 OR year > 4;
DELETE FROM timetables WHERE semester < 1 OR semester > 8;

-- Update any NULL academic_year values
UPDATE timetables SET academic_year = '2024-25' WHERE academic_year IS NULL;

-- =====================================================
-- 4. VERIFICATION QUERY
-- =====================================================

-- Run this to verify the updates worked
SELECT 
    'Timetables table updated successfully' as status,
    COUNT(*) as total_records,
    COUNT(DISTINCT department) as departments,
    COUNT(DISTINCT CONCAT(year, '-', semester)) as year_semester_combinations
FROM timetables;

-- Show sample data to verify structure
SELECT department, academic_year, year, semester, section, COUNT(*) as entries
FROM timetables 
GROUP BY department, academic_year, year, semester, section
ORDER BY department, year, semester, section
LIMIT 10;