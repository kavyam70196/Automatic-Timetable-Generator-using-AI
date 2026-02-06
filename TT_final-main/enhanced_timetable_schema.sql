-- Enhanced Timetable Schema with Conflict Prevention
-- Run this in Supabase SQL Editor

-- Update timetables table for proper conflict checking
ALTER TABLE timetables DROP CONSTRAINT IF EXISTS unique_faculty_schedule;
ALTER TABLE timetables ADD CONSTRAINT unique_faculty_schedule 
    UNIQUE(faculty_name, day, time_slot, academic_year);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_timetables_faculty_schedule 
    ON timetables(faculty_name, day, time_slot);
CREATE INDEX IF NOT EXISTS idx_timetables_dept_section_schedule 
    ON timetables(department, section, day, time_slot);

-- Function to check faculty conflicts
CREATE OR REPLACE FUNCTION check_faculty_conflict(
    p_faculty_name TEXT,
    p_day TEXT,
    p_time_slot INTEGER,
    p_academic_year TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM timetables 
        WHERE faculty_name = p_faculty_name 
        AND day = p_day 
        AND time_slot = p_time_slot 
        AND academic_year = p_academic_year
        AND is_finalized = true
    );
END;
$$ LANGUAGE plpgsql;

-- Function to check same subject on same day
CREATE OR REPLACE FUNCTION check_subject_same_day(
    p_department TEXT,
    p_section TEXT,
    p_day TEXT,
    p_subject_name TEXT,
    p_academic_year TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM timetables 
        WHERE department = p_department 
        AND section = p_section 
        AND day = p_day 
        AND subject_name = p_subject_name 
        AND academic_year = p_academic_year
    );
END;
$$ LANGUAGE plpgsql;