# MIT Mysore Timetable System - Setup Instructions

## 🚀 Quick Setup

### 1. Database Setup
Run this SQL in your Supabase SQL Editor:
```sql
-- Run cross_department_database_updates.sql
```

### 2. Start the System
```bash
python flask_server.py
```

### 3. Access the System
- **Dashboard:** http://localhost:5000/dashboard.htm
- **Subject Management:** http://localhost:5000/subject.htm
- **Timetable Generator:** http://localhost:5000/timetable-new.htm

## ✨ New Features

### Cross-Department Subjects
1. In `subject.htm`, check "Cross-Department Subject"
2. Select the teaching department
3. Faculty will automatically load from that department during timetable generation

### Enhanced Scheduling
- **Free periods:** Automatically placed in Period 6 only
- **Labs:** 2-hour continuous blocks with conflict prevention
- **Faculty conflicts:** College-wide checking prevents double-booking
- **Theory subjects:** No same subject repetition per day

### Finalize & Save
- Validates all conflicts before saving
- Stores complete timetable data in Supabase
- Faculty can download individual schedules

## 🔧 Fixed Issues
- ✅ Syntax errors in flask_server.py
- ✅ Database schema compatibility
- ✅ Cross-department faculty loading
- ✅ Enhanced conflict prevention
- ✅ Proper free period placement
- ✅ Lab scheduling rules

The system now provides complete cross-department support with robust conflict prevention.