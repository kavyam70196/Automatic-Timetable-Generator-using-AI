-- Fix Database Schema Issues for MIT Mysore Timetable System
-- Run this in Supabase SQL Editor to fix the 'type' column issue

-- =====================================================
-- 1. ADD MISSING TYPE COLUMN TO TIMETABLES TABLE
-- =====================================================

-- Check if type column exists, if not add it
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'timetables' AND column_name = 'type'
    ) THEN
        ALTER TABLE timetables ADD COLUMN type VARCHAR(20) DEFAULT 'theory' 
            CHECK (type IN ('theory', 'lab', 'free'));
        RAISE NOTICE 'Added type column to timetables table';
    ELSE
        RAISE NOTICE 'Type column already exists in timetables table';
    END IF;
END $$;

-- =====================================================
-- 2. ENSURE ALL REQUIRED COLUMNS EXIST
-- =====================================================

-- Add any missing columns
DO $$ 
BEGIN
    -- Check and add academic_year column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'timetables' AND column_name = 'academic_year'
    ) THEN
        ALTER TABLE timetables ADD COLUMN academic_year VARCHAR(10) NOT NULL DEFAULT '2024-25';
    END IF;

    -- Check and add year column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'timetables' AND column_name = 'year'
    ) THEN
        ALTER TABLE timetables ADD COLUMN year INTEGER NOT NULL DEFAULT 3 
            CHECK (year >= 1 AND year <= 4);
    END IF;

    -- Check and add semester column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'timetables' AND column_name = 'semester'
    ) THEN
        ALTER TABLE timetables ADD COLUMN semester INTEGER NOT NULL DEFAULT 5 
            CHECK (semester >= 1 AND semester <= 8);
    END IF;
END $$;

-- =====================================================
-- 3. UPDATE EXISTING DATA
-- =====================================================

-- Update any NULL type values
UPDATE timetables SET type = 'theory' WHERE type IS NULL;

-- Update any NULL academic_year values
UPDATE timetables SET academic_year = '2024-25' WHERE academic_year IS NULL;

-- Update any NULL year values
UPDATE timetables SET year = 3 WHERE year IS NULL;

-- Update any NULL semester values  
UPDATE timetables SET semester = 5 WHERE semester IS NULL;

-- =====================================================
-- 4. REFRESH SCHEMA CACHE
-- =====================================================

-- Force Supabase to refresh its schema cache
NOTIFY pgrst, 'reload schema';

-- =====================================================
-- 5. VERIFICATION
-- =====================================================

-- Verify the table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'timetables' 
ORDER BY ordinal_position;

-- Show sample data to verify
SELECT department, academic_year, year, semester, section, type, COUNT(*) as entries
FROM timetables 
GROUP BY department, academic_year, year, semester, section, type
ORDER BY department, year, semester, section
LIMIT 10;