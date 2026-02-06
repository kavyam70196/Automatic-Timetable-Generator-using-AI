import os
import sys
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from genetic_timetable_new import SupabaseTimetableGA
from typing import Any, Dict, List

app = Flask(__name__)
CORS(app)

@app.route('/generate', methods=['POST'])
def generate_timetable():
    """Generate a timetable for a section using genetic algorithm.
       Expected payload shape:
         { department, semester, year, academic_year, sections: [{ name, assignments: [{ subject, faculty, target_department (opt) }, ... ] }, ... ] }
    """
    try:
        payload = None
        # Prefer proper JSON content-type
        if request.is_json:
            payload = request.get_json()
        else:
            raw = request.get_data(as_text=True)
            if raw:
                try:
                    payload = json.loads(raw)
                except Exception:
                    return jsonify({'error': 'Invalid JSON body'}), 400
            else:
                return jsonify({'error': 'Empty request body; JSON required'}), 400

        if not payload:
            return jsonify({'error': 'JSON body required'}), 400

        department = payload.get('department')
        semester = payload.get('semester')
        year = payload.get('year')
        academic_year = payload.get('academic_year') or payload.get('academicYear')
        sections = payload.get('sections')
        
        # Validate required parameters
        if not all([department, semester, year, academic_year, sections]):
            return jsonify({'error': 'Missing required parameters: department, semester, year, academic_year, sections'}), 400
        
        # Convert to proper types
        try:
            semester = int(semester)
            year = int(year)
        except (ValueError, TypeError):
            return jsonify({'error': 'Semester and year must be integers'}), 400
        
        # Validate ranges
        if not (1 <= semester <= 8):
            return jsonify({'error': 'Semester must be between 1 and 8'}), 400
        if not (1 <= year <= 4):
            return jsonify({'error': 'Year must be between 1 and 4'}), 400

        ga = SupabaseTimetableGA(
            supabase_url=os.getenv("SUPABASE_URL", "https://bkmzyhroignpjebfpqug.supabase.co"),
            supabase_key=os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrbXp5aHJvaWducGplYmZwcXVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc0MjA1NDUsImV4cCI6MjA3Mjk5NjU0NX0.ICE2eYzFZvz0dtNpAa5YlJTZD-idc2J76wn1ZeHwwck")
        )
        results: Dict[str, Any] = {}
        generated_timetables: List[Dict[str, Any]] = []
        for sec in sections:
            sec_name = sec.get('name') or sec.get('section') or 'A'
            assignments = sec.get('assignments') or sec.get('data') or sec
            
            # Pass timetables generated so far in this batch for conflict checking
            res = ga.evolve_section(
                department=department, 
                section=sec_name, 
                section_data=assignments,
                # Combine with timetables generated in this run
                other_timetables=generated_timetables 
            )
            
            timetable = res.get('timetable')
            if isinstance(timetable, dict) and res.get('valid'):
                # Add section and department info for saving later
                res['section_name'] = sec_name
                res['department'] = department
                generated_timetables.append(res)

            results[sec_name] = res

        # After generating all, save the valid ones to Supabase
        for result in generated_timetables:
            timetable_data = result.get('timetable')
            section_name = result.get('section_name')
            department_name = result.get('department')
            if result.get('valid') and timetable_data is not None and section_name is not None and department_name is not None:
                try:
                    ga.save_to_supabase(
                        timetable=timetable_data,
                        section=section_name,
                        department=department_name,
                        academic_year=academic_year,
                        year=year,
                        semester=semester
                    )
                    print(f"Saved timetable for {department_name} {section_name} Y{year}S{semester}", file=sys.stderr)
                except Exception as save_error:
                    print(f"Error saving timetable for {section_name}: {save_error}", file=sys.stderr)
                    # Don't fail the entire request if save fails
                    results[section_name]['save_error'] = str(save_error)
        return jsonify(results)
    except Exception as e:
        print(f"/generate error: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/get_timetables', methods=['GET'])
def get_timetables():
    """Get timetables for a department (strict isolation)"""
    try:
        department = request.args.get('department')
        if not department:
            return jsonify({'error': 'Department is required'}), 400
            
        ga = SupabaseTimetableGA()
        
        # STRICT: Only timetables for this department
        query = ga.supabase.table('timetables').select('*').eq('department', department)
        response = query.execute()
        
        return jsonify(response.data or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_timetable', methods=['GET'])
def get_timetable():
    """Get specific timetable"""
    try:
        department = request.args.get('department')
        year = request.args.get('year')
        semester = request.args.get('semester')
        section = request.args.get('section')
        
        ga = SupabaseTimetableGA()
        query = ga.supabase.table('timetables').select('*')
        
        if department: query = query.eq('department', department)
        if year: query = query.eq('year', int(year))
        if semester: query = query.eq('semester', int(semester))
        if section: query = query.eq('section', section)
        
        response = query.execute()
        return jsonify(response.data or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_faculty_timetable', methods=['GET'])
def get_faculty_timetable():
    """Get timetable for a specific faculty (enhanced for cross-department)"""
    try:
        faculty_name = request.args.get('faculty_name')
        academic_year = request.args.get('academic_year')
        department = request.args.get('department')
        
        if not faculty_name:
            return jsonify({'error': 'Faculty name is required'}), 400
            
        ga = SupabaseTimetableGA()
        query = ga.supabase.table('timetables').select('*').eq('faculty_name', faculty_name)
        
        if academic_year:
            query = query.eq('academic_year', academic_year)
        
        if department:
            # For department-based filtering, show only subjects taught by this faculty in this department
            query = query.eq('faculty_department', department)
        
        # Only get finalized timetables for faculty download
        query = query.eq('is_finalized', True)
        
        response = query.execute()
        
        # Organize by day and time for easy display
        timetable_data = response.data or []
        organized_schedule = {}
        
        for entry in timetable_data:
            day = entry['day']
            time_slot = entry['time_slot']
            
            if day not in organized_schedule:
                organized_schedule[day] = {}
            
            organized_schedule[day][time_slot] = {
                'subject_name': entry['subject_name'],
                'subject_code': entry['subject_code'],
                'section': entry['section'],
                'room': entry['room'],
                'department': entry['department'],
                'type': entry['type'],
                'is_cross_dept': entry.get('is_cross_dept', False)
            }
        
        return jsonify({
            'faculty_name': faculty_name,
            'schedule': organized_schedule,
            'raw_data': timetable_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_assignments', methods=['POST'])
def save_assignments():
    """Accept finalized payload from frontend and persist assignments into Supabase 'faculty_assignments' table.
       Expected payload shape:
         { department, year, semester, academic_year, sections: [{ name, assignments: [{ subject, faculty, target_department (opt) }, ... ] }, ... ] }
    """
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON required'}), 400
        ga = SupabaseTimetableGA(
            supabase_url=os.getenv("SUPABASE_URL", "https://bkmzyhroignpjebfpqug.supabase.co"),
            supabase_key=os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrbXp5aHJvaWducGplYmZwcXVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc0MjA1NDUsImV4cCI6MjA3Mjk5NjU0NX0.ICE2eYzFZvz0dtNpAa5YlJTZD-idc2J76wn1ZeHwwck")
        )
        dept = payload.get('department')
        year = payload.get('year')
        semester = payload.get('semester')
        academic_year = payload.get('academic_year') or payload.get('academicYear')
        sections = payload.get('sections') or []
        rows = []
        for sec in sections:
            sec_name = sec.get('name') or sec.get('section')
            assigns = sec.get('assignments') or []
            for a in assigns:
                # Get subject and faculty IDs from database
                subject_code = a.get('subject') or a.get('sub_code') or a.get('subject_code')
                faculty_name = a.get('faculty') or a.get('faculty_name') or a.get('facultyName')
                
                # Find subject ID
                subject_query = ga.supabase.table('subjects').select('id').eq('sub_code', subject_code).eq('department', dept).execute()
                if not subject_query.data:
                    subject_query = ga.supabase.table('subjects').select('id').eq('name', subject_code).eq('department', dept).execute()
                
                # Find faculty ID - search across all departments for cross-department subjects
                faculty_query = ga.supabase.table('faculty').select('id').eq('name', faculty_name).execute()
                if not faculty_query.data:
                    # Try with department filter as fallback
                    faculty_query = ga.supabase.table('faculty').select('id').eq('name', faculty_name).eq('department', dept).execute()
                
                if subject_query.data and faculty_query.data:
                    rows.append({
                        'subject_id': subject_query.data[0]['id'],
                        'faculty_id': faculty_query.data[0]['id'],
                        'section': sec_name,
                        'academic_year': academic_year
                    })
        
        # insert into faculty_assignments table
        if rows:
            try:
                # Clear existing assignments for this configuration
                ga.supabase.table('faculty_assignments').delete().eq('academic_year', academic_year).execute()
                # Insert new assignments
                ga.supabase.table('faculty_assignments').insert(rows).execute()
            except Exception as e:
                print(f"Error saving assignments: {e}", file=sys.stderr)
        return jsonify({'status': 'ok', 'inserted': len(rows)})
    except Exception as e:
        print(f"/save_assignments error: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@app.route('/get_subjects', methods=['GET'])
def get_subjects():
    """Get subjects for a department (strict isolation)"""
    try:
        department = request.args.get('department')
        if not department:
            return jsonify({'error': 'Department is required'}), 400
            
        ga = SupabaseTimetableGA()
        
        # STRICT: Only subjects belonging to this department
        query = ga.supabase.table('subjects').select('*').eq('department', department)
        response = query.execute()
        
        return jsonify(response.data or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_faculty', methods=['GET'])
def get_faculty():
    """Get faculty for a department (strict isolation unless cross-department)"""
    try:
        department = request.args.get('department')
        if not department:
            return jsonify({'error': 'Department is required'}), 400
            
        ga = SupabaseTimetableGA()
        
        # STRICT: Only faculty from requested department
        query = ga.supabase.table('faculty').select('*').eq('department', department)
        response = query.execute()
        
        return jsonify(response.data or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_departments', methods=['GET'])
def get_departments():
    """Get all available departments"""
    try:
        ga = SupabaseTimetableGA()
        response = ga.supabase.table('departments').select('*').order('name').execute()
        return jsonify(response.data or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_faculty_for_subject', methods=['POST'])
def get_faculty_for_subject():
    """Get faculty for a specific subject (handles cross-department)"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON required'}), 400
            
        subject_code = payload.get('subject_code')
        department = payload.get('department')
        
        ga = SupabaseTimetableGA()
        
        # Get subject details to check if cross-department
        subject_query = ga.supabase.table('subjects').select('is_cross_dept,teaching_dept').eq('sub_code', subject_code).eq('department', department).execute()
        
        if not subject_query.data:
            subject_query = ga.supabase.table('subjects').select('is_cross_dept,teaching_dept').eq('name', subject_code).eq('department', department).execute()
        
        if subject_query.data:
            subject = subject_query.data[0]
            target_dept = subject.get('teaching_dept') if subject.get('is_cross_dept') else department
        else:
            target_dept = department
        
        # Get faculty from target department
        faculty_query = ga.supabase.table('faculty').select('*').eq('department', target_dept).execute()
        
        return jsonify({
            'faculty': faculty_query.data or [],
            'target_department': target_dept,
            'is_cross_dept': subject_query.data[0].get('is_cross_dept', False) if subject_query.data else False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/swap_classes', methods=['POST'])
def swap_classes():
    """Handle class swapping with enhanced conflict detection"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON required'}), 400
            
        department = payload.get('department')
        section = payload.get('section')
        swap_data = payload.get('swap_data')
        academic_year = payload.get('academic_year')
        
        ga = SupabaseTimetableGA()
        
        # Enhanced conflict checking
        faculty1 = swap_data.get('faculty1')
        faculty2 = swap_data.get('faculty2')
        day1 = swap_data.get('day1')
        slot1 = swap_data.get('slot1')
        day2 = swap_data.get('day2')
        slot2 = swap_data.get('slot2')
        
        # Check ALL faculty conflicts across entire college
        conflict_query1 = ga.supabase.table('timetables').select('*').eq('faculty_name', faculty1).eq('day', day2).eq('time_slot', slot2).eq('academic_year', academic_year).execute()
        conflict_query2 = ga.supabase.table('timetables').select('*').eq('faculty_name', faculty2).eq('day', day1).eq('time_slot', slot1).eq('academic_year', academic_year).execute()
        
        conflicts = []
        if conflict_query1.data:
            conflicts.extend([{'faculty': faculty1, 'conflict_with': c} for c in conflict_query1.data])
        if conflict_query2.data:
            conflicts.extend([{'faculty': faculty2, 'conflict_with': c} for c in conflict_query2.data])
        
        if conflicts:
            return jsonify({
                'success': False,
                'error': 'Faculty conflict detected across college',
                'conflicts': conflicts
            })
        
        return jsonify({'success': True, 'message': 'Swap is valid - no conflicts detected'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_faculty_conflicts', methods=['POST'])
def check_faculty_conflicts():
    """Check for faculty conflicts before assignment"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON required'}), 400
            
        ga = SupabaseTimetableGA()
        
        faculty_name = payload.get('faculty_name')
        day = payload.get('day')
        time_slot = payload.get('time_slot')
        academic_year = payload.get('academic_year')
        
        # Check for conflicts using database function
        conflict_query = ga.supabase.rpc('check_faculty_conflict', {
            'p_faculty_name': faculty_name,
            'p_day': day,
            'p_time_slot': time_slot,
            'p_academic_year': academic_year
        }).execute()
        
        has_conflict = conflict_query.data if conflict_query.data else False
        
        return jsonify({
            'has_conflict': has_conflict,
            'faculty': faculty_name,
            'day': day,
            'time_slot': time_slot
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/finalize_timetable', methods=['POST'])
def finalize_timetable():
    """Finalize and permanently save timetables with enhanced conflict checking"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON required'}), 400
            
        ga = SupabaseTimetableGA()
        
        department = payload.get('department')
        academic_year = payload.get('academic_year')
        year = payload.get('year')
        semester = payload.get('semester')
        timetable_data = payload.get('timetable_data', [])
        
        # Enhanced conflict validation
        conflicts = []
        subject_day_check = {}
        
        for entry in timetable_data:
            faculty_name = entry.get('faculty_name')
            day = entry.get('day')
            time_slot = entry.get('time_slot')
            subject_name = entry.get('subject_name')
            section = entry.get('section')
            subject_type = entry.get('type', 'theory')
            
            # Rule 1: Check faculty conflicts
            conflict_check = ga.supabase.rpc('check_faculty_conflict', {
                'p_faculty_name': faculty_name,
                'p_day': day,
                'p_time_slot': time_slot,
                'p_academic_year': academic_year
            }).execute()
            
            if conflict_check.data:
                conflicts.append(f"Faculty {faculty_name} conflict on {day} P{time_slot}")
            
            # Rule 2: Free hours only in P6
            if subject_type.lower() == 'free' and time_slot != 6:
                conflicts.append(f"Free period must be in P6, found in P{time_slot}")
            
            # Rule 3: Same subject not repeated on same day (for theory subjects)
            if subject_type.lower() == 'theory':
                day_subject_key = f"{section}-{day}-{subject_name}"
                if day_subject_key in subject_day_check:
                    conflicts.append(f"Theory subject {subject_name} repeated on {day} for section {section}")
                subject_day_check[day_subject_key] = True
        
        if conflicts:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'conflicts': conflicts
            }), 400
        
        # First, delete any existing finalized entries for this configuration
        ga.supabase.table('timetables').delete().match({
            'department': department,
            'academic_year': academic_year,
            'year': year,
            'semester': semester,
            'is_finalized': True
        }).execute()
        
        # Save timetable entries
        for entry in timetable_data:
            # Get faculty department info
            faculty_dept = entry.get('faculty_department') or department
            
            ga.supabase.table('timetables').insert({
                'department': department,
                'section': entry.get('section'),
                'day': entry.get('day'),
                'time_slot': entry.get('time_slot'),
                'subject_name': entry.get('subject_name'),
                'subject_code': entry.get('subject_code'),
                'faculty_name': entry.get('faculty_name'),
                'faculty_department': faculty_dept,
                'room': entry.get('room'),
                'type': entry.get('type'),
                'academic_year': academic_year,
                'year': year,
                'semester': semester,
                'is_cross_dept': entry.get('is_cross_dept', False),
                'teaching_dept': entry.get('teaching_dept'),
                'is_finalized': True
            }).execute()
        
        return jsonify({
            'success': True,
            'message': 'Timetables finalized successfully',
            'saved_count': len(timetable_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard_stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        department = request.args.get('department')
        ga = SupabaseTimetableGA()
        
        # Get timetables count
        timetables_query = ga.supabase.table('timetables').select('*')
        if department:
            timetables_query = timetables_query.eq('department', department)
        timetables_response = timetables_query.execute()
        timetables = timetables_response.data or []
        
        # Get faculty count
        faculty_query = ga.supabase.table('faculty').select('*')
        if department:
            faculty_query = faculty_query.eq('department', department)
        faculty_response = faculty_query.execute()
        faculty = faculty_response.data or []
        
        # Get subjects count
        subjects_query = ga.supabase.table('subjects').select('*')
        if department:
            subjects_query = subjects_query.eq('department', department)
        subjects_response = subjects_query.execute()
        subjects = subjects_response.data or []
        
        # Calculate statistics
        total_timetables = len(timetables)
        finalized_timetables = len([t for t in timetables if t.get('is_finalized')])
        active_timetables = total_timetables - finalized_timetables
        
        return jsonify({
            'total_timetables': total_timetables,
            'finalized_timetables': finalized_timetables,
            'active_timetables': active_timetables,
            'total_faculty': len(faculty),
            'total_subjects': len(subjects),
            'completion_rate': round((finalized_timetables / total_timetables * 100) if total_timetables > 0 else 0, 1)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/validate_timetable_rules', methods=['POST'])
def validate_timetable_rules():
    """Validate timetable against all rules before saving"""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON required'}), 400
            
        ga = SupabaseTimetableGA()
        timetable_data = payload.get('timetable_data', [])
        
        violations = []
        
        # Group by section and day for validation
        section_day_subjects = {}
        faculty_schedule = {}
        
        for entry in timetable_data:
            section = entry.get('section')
            day = entry.get('day')
            time_slot = entry.get('time_slot')
            subject_name = entry.get('subject_name')
            faculty_name = entry.get('faculty_name')
            subject_type = entry.get('type', 'theory')
            
            # Rule 1: Free periods only in P6
            if subject_type.lower() == 'free' and time_slot != 6:
                violations.append(f"Free period found in P{time_slot} on {day}, must be in P6")
            
            # Rule 2: Same subject not repeated on same day
            section_day_key = f"{section}-{day}"
            if section_day_key not in section_day_subjects:
                section_day_subjects[section_day_key] = set()
            
            if subject_name in section_day_subjects[section_day_key] and subject_name != 'FREE':
                violations.append(f"Subject {subject_name} repeated on {day} for section {section}")
            section_day_subjects[section_day_key].add(subject_name)
            
            # Rule 3: Faculty conflicts
            faculty_time_key = f"{faculty_name}-{day}-{time_slot}"
            if faculty_time_key in faculty_schedule and faculty_name != 'N/A':
                violations.append(f"Faculty {faculty_name} conflict on {day} P{time_slot}")
            faculty_schedule[faculty_time_key] = True
        
        return jsonify({
            'valid': len(violations) == 0,
            'violations': violations,
            'total_entries': len(timetable_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/system_health', methods=['GET'])
def system_health():
    """Check system health and connectivity"""
    try:
        ga = SupabaseTimetableGA()
        
        # Test database connection
        test_query = ga.supabase.table('subjects').select('count').limit(1).execute()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': time.time(),
            'message': 'All systems operational'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'timestamp': time.time(),
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting MIT Mysore Timetable Server (Enhanced)...")
    print("Server running on http://localhost:5000")
    print("Dashboard: http://localhost:5000/dashboard.htm")
    print("Timetable Generator: http://localhost:5000/timetable-new.htm")
    print("Features: Cross-department subjects, Faculty conflict checking, Enhanced scheduling")
    app.run(debug=True, port=5000, host='0.0.0.0')
