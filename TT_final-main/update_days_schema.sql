-- Update database schema to support Tuesday-Saturday schedule
-- Run this in Supabase SQL Editor

-- Drop existing day constraint if it exists
DO $$ 
BEGIN
    -- Remove old day constraint
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name LIKE '%day%' 
        AND table_name = 'timetables'
        AND constraint_type = 'CHECK'
    ) THEN
        ALTER TABLE timetables DROP CONSTRAINT IF EXISTS timetables_day_check;
    END IF;
END $$;

-- Add new day constraint for Tuesday-Saturday
ALTER TABLE timetables ADD CONSTRAINT timetables_day_check 
    CHECK (day IN ('Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'));

-- Update any existing Monday entries to Tuesday (if any)
UPDATE timetables SET day = 'Tuesday' WHERE day = 'Monday';

-- Verify the constraint
SELECT 
    'Day constraint updated successfully' as status,
    'Timetables now support Tuesday-Saturday schedule' as message,
    NOW() as updated_at;