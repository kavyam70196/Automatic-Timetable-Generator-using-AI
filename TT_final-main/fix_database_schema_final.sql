-- Add is_finalized column if it does not exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'timetables' 
          AND column_name = 'is_finalized'
          AND table_schema = 'public'
    ) THEN
        ALTER TABLE public.timetables 
        ADD COLUMN is_finalized BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added is_finalized column to timetables table';
    ELSE
        RAISE NOTICE 'is_finalized column already exists';
    END IF;
END $$ LANGUAGE plpgsql;

-- Update existing NULL values to FALSE
UPDATE public.timetables 
SET is_finalized = FALSE 
WHERE is_finalized IS NULL;

-- Verify schema fix
SELECT 
    'Schema Fix Complete' AS status,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN is_finalized = TRUE THEN 1 END) AS finalized_count,
    COUNT(CASE WHEN is_finalized = FALSE THEN 1 END) AS draft_count
FROM public.timetables;
