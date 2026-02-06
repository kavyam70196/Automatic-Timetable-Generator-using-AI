-- Cross-Department Functionality Verification Queries
-- Run these queries to verify your cross-department setup

-- 1. Check faculty distribution across departments
SELECT department, COUNT(*) as faculty_count 
FROM faculty 
GROUP BY department 
ORDER BY department;

-- 2. Check cross-department subjects
SELECT 
    name,
    department,
    is_cross_dept,
    teaching_dept,
    sub_code
FROM subjects 
WHERE is_cross_dept = true;

-- 3. Verify faculty conflict checking function
SELECT check_faculty_conflict('FACULTY_ID', 'MON', 'P1') as has_conflict;

-- 4. Verify same subject checking function
SELECT check_same_subject_same_day('SUBJECT_ID', 'SECTION_ID', 'MON') as same_subject_exists;