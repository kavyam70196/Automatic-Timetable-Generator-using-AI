import os
import sys
import random
import json
from typing import List, Dict, Any, Optional, Tuple

try:
    from supabase._sync.client import create_client
except ImportError:
    from supabase.client import create_client

os.environ.pop('http_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTPS_PROXY', None)

class SupabaseTimetableGA:
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url or "https://bkmzyhroignpjebfpqug.supabase.co"
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrbXp5aHJvaWducGplYmZwcXVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc0MjA1NDUsImV4cCI6MjA3Mjk5NjU0NX0.ICE2eYzFZvz0dtNpAa5YlJTZD-idc2J76wn1ZeHwwck"
        if not self.supabase_key:
            raise ValueError("Supabase key is required")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        self.days = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        self.time_slots = [
            {'start': '09:00', 'end': '10:00', 'slot_id': 1, 'name': 'Period 1'},
            {'start': '10:00', 'end': '11:00', 'slot_id': 2, 'name': 'Period 2'},
            {'start': '11:15', 'end': '12:15', 'slot_id': 3, 'name': 'Period 3'},
            {'start': '12:15', 'end': '13:15', 'slot_id': 4, 'name': 'Period 4'},
            {'start': '14:00', 'end': '15:00', 'slot_id': 5, 'name': 'Period 5'},
            {'start': '15:00', 'end': '16:00', 'slot_id': 6, 'name': 'Period 6'}
        ]
        self.continuous_slots = [[1, 2], [3, 4], [5, 6]]

    def fetch_data(self, department: Optional[str] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        try:
            subj_q = self.supabase.table('subjects').select('*')
            if department:
                subj_q = subj_q.eq('department', department)
            subjects_resp = subj_q.execute()
            subjects = subjects_resp.data or []

            fac_q = self.supabase.table('faculty').select('*')
            faculty_resp = fac_q.execute()
            faculty = faculty_resp.data or []

            tt_resp = self.supabase.table('timetables').select('*').execute()
            existing_timetables = tt_resp.data or []

            return subjects, faculty, existing_timetables
        except Exception as e:
            print(f"fetch_data error: {e}", file=sys.stderr)
            return [], [], []

    def get_subject_hours_from_db(self, department: Optional[str], subject_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        try:
            for code in subject_codes:
                if not code:
                    continue
                    
                q = self.supabase.table('subjects').select('weekly_hours,type,sub_code,name,is_cross_dept,teaching_dept,classes_per_week')
                if department:
                    q = q.eq('department', department)
                q = q.eq('sub_code', code)
                resp = q.execute()
                
                if not (resp.data and len(resp.data) > 0):
                    q2 = self.supabase.table('subjects').select('weekly_hours,type,sub_code,name,is_cross_dept,teaching_dept,classes_per_week')
                    if department:
                        q2 = q2.eq('department', department)
                    q2 = q2.eq('name', code)
                    resp = q2.execute()
                
                if resp.data and len(resp.data) > 0:
                    sd = resp.data[0]
                    weekly = int(sd.get('weekly_hours', 3))
                    classes_per_week = int(sd.get('classes_per_week', weekly))
                    typ = (sd.get('type') or 'theory').lower()
                    
                    result[code] = {
                        'weekly_hours': weekly, 
                        'classes_per_week': classes_per_week,
                        'type': typ,
                        'sub_code': sd.get('sub_code', code),
                        'name': sd.get('name', code),
                        'is_cross_dept': sd.get('is_cross_dept', False),
                        'teaching_dept': sd.get('teaching_dept')
                    }
                else:
                    result[code] = {
                        'weekly_hours': 3, 
                        'classes_per_week': 3,
                        'type': 'theory',
                        'sub_code': code,
                        'name': code,
                        'is_cross_dept': False,
                        'teaching_dept': None
                    }
            return result
        except Exception as e:
            print(f"get_subject_hours_from_db error: {e}", file=sys.stderr)
            return {code: {'weekly_hours': 3, 'classes_per_week': 3, 'type': 'theory', 'sub_code': code, 'name': code, 'is_cross_dept': False, 'teaching_dept': None} for code in subject_codes if code}

    def check_faculty_conflict(self, faculty_name: Optional[str], day: str, slot_id: int) -> bool:
        if not faculty_name or faculty_name == 'N/A':
            return False
        
        try:
            response = self.supabase.table('timetables').select('*').eq('faculty_name', faculty_name).eq('day', day).eq('time_slot', slot_id).execute()
            return bool(response.data and len(response.data) > 0)
        except Exception as e:
            print(f"Error checking faculty conflicts: {e}", file=sys.stderr)
            return False

    def evolve_section(self, department: str, section: str, section_data: List[Dict[str, Any]], other_timetables: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        assignments = []
        for a in section_data:
            subj = a.get('subject') or a.get('sub_code') or a.get('subject_code')
            fac = a.get('faculty') or a.get('faculty_name') or a.get('facultyName')
            target_dept = a.get('target_department') or a.get('targetDept') or department
            if subj:
                assignments.append({'subject_code': subj, 'faculty_name': fac, 'target_department': target_dept})

        subjects_db, faculty_db, existing_timetables_db = self.fetch_data(department=department)
        
        all_existing_faculty_slots = set()
        for tt in existing_timetables_db:
            if tt.get('faculty_name'):
                all_existing_faculty_slots.add((tt['faculty_name'], tt['day'], tt['time_slot']))
        
        if other_timetables:
            for tt_result in other_timetables:
                if tt_result.get('valid') and tt_result.get('timetable'):
                    for day, day_data in tt_result['timetable'].items():
                        for slot_id, entry in day_data.items():
                            if entry and entry.get('faculty_name'):
                                all_existing_faculty_slots.add((entry['faculty_name'], day, slot_id))

        room_number = f"Room-{section}01"
        subject_keys = [x['subject_code'] for x in assignments if x.get('subject_code')]
        subject_hours = self.get_subject_hours_from_db(department, subject_keys)

        timetable: Dict[str, Dict[int, Optional[Dict[str, Any]]]] = {d: {i: None for i in range(1, 7)} for d in self.days}
        
        subject_placement_tracker = {}
        lab_counter = 1
        
        placement_queue = []
        for a in assignments:
            code = a['subject_code']
            fac = a.get('faculty_name')
            info = subject_hours.get(code, {'classes_per_week': 3, 'type': 'theory'})
            classes = int(info.get('classes_per_week', 3))
            typ = info.get('type', 'theory').lower()
            
            target_dept = a.get('target_department', department)
            if info.get('is_cross_dept') and info.get('teaching_dept'):
                target_dept = info.get('teaching_dept')
            
            for i in range(classes):
                placement_queue.append({
                    'subject_code': code,
                    'subject_key': code.strip().upper(),
                    'faculty_name': fac,
                    'type': typ,
                    'periods': 2 if typ == 'lab' else 1,
                    'target_department': target_dept,
                    'is_cross_dept': info.get('is_cross_dept', False),
                    'teaching_dept': info.get('teaching_dept'),
                    'priority': 1 if typ == 'lab' else 2
                })
        
        placement_queue.sort(key=lambda x: (x['priority'], x['subject_key']))
        print(f"PLACEMENT QUEUE: {[(s['subject_key'], s['type']) for s in placement_queue]}", file=sys.stderr)
        
        unplaced_sessions_count = len(placement_queue)
        for session in placement_queue:
            subject_key = session['subject_key']
            faculty = session['faculty_name']
            placed = False
            
            if subject_key not in subject_placement_tracker:
                subject_placement_tracker[subject_key] = []

            used_days = subject_placement_tracker.get(subject_key, [])
            if session['type'] in ['theory', 'lab']:
                days_to_try = [day for day in self.days if day not in used_days]
            else:
                days_to_try = list(self.days)

            random.shuffle(days_to_try)

            if not days_to_try:
                print(f"ERROR: No available days for {subject_key} (type: {session['type']})", file=sys.stderr)
                continue

            for day in days_to_try:
                if session['type'] == 'lab':
                    for pair in self.continuous_slots:
                        if all(timetable[day][p] is None for p in pair):
                            if any((faculty, day, p) in all_existing_faculty_slots for p in pair) or \
                               any(self.check_faculty_conflict(faculty, day, p) for p in pair):
                                continue
                            
                            subject_placement_tracker[subject_key].append(day)
                            entry_data = {
                                'subject_code': session['subject_code'], 'subject_name': f"{session['subject_code']} Lab",
                                'faculty_name': faculty, 'section': section, 'room': f"Lab-{lab_counter}", 'type': 'lab', 'periods': 2,
                                'target_department': session.get('target_department'), 'is_cross_dept': session.get('is_cross_dept', False),
                                'teaching_dept': session.get('teaching_dept')
                            }
                            for p in pair:
                                timetable[day][p] = entry_data
                                all_existing_faculty_slots.add((faculty, day, p))
                            
                            lab_counter += 1
                            placed = True
                            unplaced_sessions_count -= 1
                            print(f"PLACED LAB: {subject_key} on {day}", file=sys.stderr)
                            break 
                else:
                    slots = [6] if subject_key == 'NSS' or session['type'] == 'free' else list(range(1, 7))
                    for slot in slots:
                        if timetable[day][slot] is None:
                            if (faculty, day, slot) in all_existing_faculty_slots or self.check_faculty_conflict(faculty, day, slot):
                                continue
                            
                            if session['type'] in ['theory', 'lab']:
                                subject_placement_tracker[subject_key].append(day)

                            entry_data = {
                                'subject_code': session['subject_code'], 'subject_name': session['subject_code'],
                                'faculty_name': faculty, 'section': section, 'room': room_number,
                                'type': session['type'], 'periods': 1,
                                'target_department': session.get('target_department'), 'is_cross_dept': session.get('is_cross_dept', False),
                                'teaching_dept': session.get('teaching_dept')
                            }
                            timetable[day][slot] = entry_data
                            all_existing_faculty_slots.add((faculty, day, slot))
                            placed = True
                            unplaced_sessions_count -= 1
                            print(f"PLACED {session['type'].upper()}: {subject_key} on {day} slot {slot}", file=sys.stderr)
                            break
                
                if placed:
                    break
        
        empty_slots = sum(1 for day_slots in timetable.values() for entry in day_slots.values() if entry is None)
        if unplaced_sessions_count > 0 or empty_slots > 0:
            error_msg = f"Failed to generate a complete timetable. Unplaced sessions: {unplaced_sessions_count}. Empty slots: {empty_slots}."
            print(f"VALIDATION FAILED: {error_msg}", file=sys.stderr)
            # Return the partially generated timetable for debugging, but mark as invalid
            return {'valid': False, 'error': error_msg, 'timetable': timetable}

        print("Successfully generated a complete and valid timetable.", file=sys.stderr)
        return {'valid': True, 'timetable': timetable, 'section_name': section, 'department': department}

    def save_to_supabase(self, timetable: Dict[str, Dict[int, Any]], section: str, department: str,
                         academic_year: str, year: int, semester: int) -> None:
        rows = []
        processed_labs = set()
        
        for day in self.days:
            for slot_id in range(1, 7):
                entry = timetable[day].get(slot_id)
                
                if not entry:
                    continue
                
                if entry.get('type') == 'lab':
                    lab_key = f"{day}-{entry.get('subject_code')}-{section}"
                    if lab_key in processed_labs:
                        continue
                    processed_labs.add(lab_key)
                
                faculty_dept = department
                if entry and entry.get('is_cross_dept') and entry.get('teaching_dept'):
                    faculty_dept = entry.get('teaching_dept')
                
                entry_type = entry.get('type', 'theory')
                
                rows.append({
                    'department': department,
                    'section': section,
                    'day': day,
                    'time_slot': slot_id,
                    'subject_code': entry.get('subject_code'),
                    'subject_name': entry.get('subject_name') or entry.get('subject_code'),
                    'faculty_name': entry.get('faculty_name'),
                    'faculty_department': faculty_dept,
                    'room': entry.get('room'),
                    'academic_year': academic_year,
                    'year': int(year),
                    'semester': int(semester),
                    'type': entry_type,
                    'is_cross_dept': entry.get('is_cross_dept', False),
                    'teaching_dept': entry.get('teaching_dept'),
                    'is_finalized': False
                })

        try:
            del_q = self.supabase.table('timetables').delete()
            del_q = del_q.eq('department', department).eq('section', section)
            del_q = del_q.eq('academic_year', academic_year)
            del_q = del_q.eq('year', int(year))
            del_q = del_q.eq('semester', int(semester))
            
            del_response = del_q.execute()
            print(f"Deleted {len(del_response.data) if del_response.data else 0} existing entries", file=sys.stderr)
            
            if rows:
                insert_response = self.supabase.table('timetables').insert(rows).execute()
                print(f"Inserted {len(insert_response.data) if insert_response.data else 0} new entries", file=sys.stderr)
                
        except Exception as e:
            print(f"save_to_supabase error: {e}", file=sys.stderr)
            raise e