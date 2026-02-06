# Department Isolation Test Guide

## Test Cross-Department Faculty Loading

### Step 1: Create Test Data
```sql
-- In Supabase SQL Editor
-- Create a cross-department subject in ISE
INSERT INTO subjects (department, academic_year, year, semester, name, is_cross_dept, teaching_dept) 
VALUES ('ISE', '2024-25', 2, 3, 'Engineering Mathematics', true, 'MATH');

-- Verify MATH faculty exists
SELECT * FROM faculty WHERE department = 'MATH';
```

### Step 2: Test Department Login
1. **Login to ISE Department**
2. **Load Subjects** - Should see ISE subjects including "Engineering Mathematics"
3. **Assign Faculty** - For "Engineering Mathematics", dropdown should show MATH faculty only

### Step 3: Verify Isolation
1. **Login to CSE Department** 
2. **Should NOT see**:
   - ISE subjects
   - ISE faculty
   - ISE timetables

### Expected Console Output
```
=== FACULTY LOADING DEBUG ===
Subject: Engineering Mathematics
Is Cross Dept: true
Teaching Dept: MATH
Current Dept: ISE
Department to fetch: MATH
Found faculty count: 3
Faculty names: ["Dr. Ramesh Babu", "Dr. Sushma Rao", "Mr. Naveen Kumar"]
=== END DEBUG ===
```

### If Still Not Working
1. Check browser console for debug logs
2. Verify database has:
   - `is_cross_dept = true`
   - `teaching_dept = 'MATH'` (exact department code)
3. Verify MATH faculty exists in database
4. Check field names match exactly: `is_cross_dept`, `teaching_dept`

## Current Fix Applied
- ✅ Strict department isolation (each dept sees only their data)
- ✅ Cross-department exception (shows other dept faculty only when subject is cross-dept)
- ✅ Enhanced debugging logs
- ✅ Backend department filtering
- ✅ Proper field name usage