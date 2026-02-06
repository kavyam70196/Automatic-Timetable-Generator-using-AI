# MIT Mysore Timetable System

## Complete Integrated System

### Quick Start
1. **Test**: `python test_supabase_connection.py`
2. **Start**: `START_SYSTEM.bat` or `python flask_server.py`
3. **Use**: `index.htm` → `page.htm` → Data Entry → Generate

### Complete Workflow
1. **Login**: `index.htm` - Select department
2. **Dashboard**: `page.htm` - Main navigation
3. **Data Entry**:
   - `subject.htm` - Add subjects with hours/type
   - `faculty.htm` - Add faculty with designations
4. **Generate**: `timetable-new.htm` → `enhanced.htm`

### Features
- ✅ Complete data management (subjects + faculty)
- ✅ Real-time Supabase integration
- ✅ 6-period structure with proper breaks
- ✅ 2-hour continuous lab scheduling
- ✅ Faculty conflict prevention
- ✅ Cross-department support
- ✅ Save/load/view timetables

### Files
- `genetic_timetable.py` - Core algorithm
- `flask_server.py` - Backend API
- `page.htm` - Main dashboard
- `subject.htm` - Subject management
- `faculty.htm` - Faculty management
- `timetable-new.htm` - Assignment setup
- `enhanced.htm` - Generation + display

**System is fully integrated and production ready!**