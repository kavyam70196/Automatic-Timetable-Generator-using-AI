import os
import sys
import random
import json
from typing import List, Dict, Any, Optional, Tuple

# Use explicit client import to satisfy Pylance
from supabase.client import create_client  # type: ignore

# Unset proxy env vars that break supabase client in some environments
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
            {'start': '09:00', 'end': '10:00', 'slot_id': 0, 'name': 'Period 1'},
            {'start': '10:00', 'end': '11:00', 'slot_id': 1, 'name': 'Period 2'},
            {'start': '11:15', 'end': '12:15', 'slot_id': 2, 'name': 'Period 3'},
            {'start': '12:15', 'end': '13:15', 'slot_id': 3, 'name': 'Period 4'},
            {'start': '14:00', 'end': '15:00', 'slot_id': 4, 'name': 'Period 5'},
            {'start': '15:00', 'end': '16:00', 'slot_id': 5, 'name': 'Period 6'}
        ]
        # Continuous 2-slot groups for labs (respecting breaks)
        self.continuous_slots = [[0, 1], [2, 3], [4, 5]]  # P1-P2, P3-P4, P5-P6

    def fetch_data(self, department: Optional[str] = None, section: Optional[str] = None,
                   academic_year: Optional[str] = None, year: Optional[int] = None,
                   semester: Optional[int] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Fetch subjects, faculty and existing timetables for conflict checking.
           Also build faculty_unavailability map (day,slot pairs) for quick checks.
        """
        try:
            subj_q = self.supabase.table('subjects').select('*')
            if department:
                subj_q = subj_q.eq('department', department)
            if academic_year:
                subj_q = subj_q.eq('academic_year', academic_year)
            if year is not None:
                subj_q = subj_q.eq('year', int(year))
            if semester is not None:
                subj_q = subj_q.eq('semester', int(semester))
            subjects_resp = subj_q.execute()
            subjects = subjects_resp.data or []

            fac_q = self.supabase.table('faculty').select('*')
            if department:
                fac_q = fac_q.eq('department', department)
            faculty_resp = fac_q.execute()
            faculty = faculty_resp.data or []

            # Build faculty unavailability mapping expected as list of {day, slot} in faculty.unavailable_slots
            faculty_unavailability = {}
            for f in faculty:
                name = f.get('name') or f.get('faculty_name') or f.get('faculty')
                unavail = f.get('unavailable_slots') or f.get('unavailability') or []
                mapped = set()
                if isinstance(unavail, list):
                    for item in unavail:
                        if isinstance(item, dict):
                            d = item.get('day'); s = item.get('slot')
                            if d is not None and s is not None:
                                try:
                                    mapped.add((d, int(s)))
                                except Exception:
                                    pass
                faculty_unavailability[name] = mapped
            # expose to instance for placement checks
            self.faculty_unavailability = faculty_unavailability

            tt_resp = self.supabase.table('timetables').select('*').execute()
            existing_timetables = tt_resp.data or []

            return subjects, faculty, existing_timetables
        except Exception as e:
            print(f"fetch_data error: {e}", file=sys.stderr)
            self.faculty_unavailability = {}
            return [], [], []

    def get_subject_hours_from_db(self, department: Optional[str], subject_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """Return mapping: subject_code -> {'weekly_hours': int, 'type': 'lab'|'theory'}."""
        result: Dict[str, Dict[str, Any]] = {}
        try:
            for code in subject_codes:
                if not code:
                    continue
                # Try by sub_code first
                q = self.supabase.table('subjects').select('weekly_hours,type,sub_code,name').eq('sub_code', code)
                if department:
                    q = q.eq('department', department)
                resp = q.execute()
                
                # If not found by sub_code, try by name
                if not (resp.data and len(resp.data) > 0):
                    q2 = self.supabase.table('subjects').select('weekly_hours,type,sub_code,name').eq('name', code)
                    if department:
                        q2 = q2.eq('department', department)
                    resp = q2.execute()
                
                if resp.data and len(resp.data) > 0:
                    sd = resp.data[0]
                    weekly = int(sd.get('weekly_hours', 3))
                    typ = (sd.get('type') or 'theory').lower()
                    result[code] = {'weekly_hours': weekly, 'type': typ}
                    print(f"Found subject {code}: {weekly}h/week, type: {typ}")
                else:
                    # Default values if not found in database
                    result[code] = {'weekly_hours': 3, 'type': 'theory'}
                    print(f"Subject {code} not found in DB, using defaults: 3h/week, theory")
            return result
        except Exception as e:
            print(f"get_subject_hours_from_db error: {e}", file=sys.stderr)
            return {code: {'weekly_hours': 3, 'type': 'theory'} for code in subject_codes if code}

    def check_faculty_conflict(self, faculty_name: Optional[str], day: str, slot_id: int, existing_timetables: List[Dict[str, Any]]) -> bool:
        """Return True if faculty is busy at (day,slot) either due to existing timetable entries or personal unavailability."""
        if not faculty_name:
            return False

        unavail = getattr(self, 'faculty_unavailability', {}).get(faculty_name) or set()
        if (day, int(slot_id)) in unavail:
            return True

        for rec in existing_timetables:
            if (rec.get('faculty_name') == faculty_name and
                rec.get('day') == day and
                int(rec.get('time_slot', -1)) == int(slot_id)):
                return True
        return False

    def check_department_conflict(self, target_department: str, day: str, slot_id: int, existing_timetables: List[Dict[str, Any]]) -> bool:
        if not target_department:
            return False
        for rec in existing_timetables:
            if (rec.get('department') == target_department and
                rec.get('day') == day and
                int(rec.get('time_slot', -1)) == int(slot_id)):
                return True
        return False

    def _place_session_with_constraints(self, timetable: Dict[str, Dict[int, Optional[Dict[str, Any]]]],
                                        session: Dict[str, Any],
                                        daily_subjects: Dict[str, set],
                                        daily_labs: Dict[str, set],
                                        section_daily_labs: Dict[str, bool],
                                        existing_timetables: List[Dict[str, Any]],
                                        section: str) -> bool:
        subject_code = session.get('subject_code')
        faculty = session.get('faculty_name')
        session_type = session.get('type')
        target_dept = session.get('target_department') or section

        if not subject_code:
            return False

        if session_type == 'lab':
            # Try to place lab in continuous 2-hour slots on different days
            available_days = []
            for day in self.days:
                # Skip if subject already scheduled on this day
                if subject_code in daily_subjects[day]:
                    continue
                # Skip if this section already has a lab on this day
                if section_daily_labs[day]:
                    continue
                # Avoid Friday for labs when possible
                if day == 'Friday':
                    continue
                available_days.append(day)
            
            # Shuffle to distribute labs across different days
            random.shuffle(available_days)
            
            for day in available_days:
                # Try each continuous slot group
                for slot_group in self.continuous_slots:
                    can_place = True
                    
                    # Check if both slots in the group are free
                    for slot in slot_group:
                        if timetable[day][slot] is not None:
                            can_place = False
                            break
                        if self.check_faculty_conflict(faculty, day, slot, existing_timetables):
                            can_place = False
                            break
                        if self.check_department_conflict(target_dept, day, slot, existing_timetables):
                            can_place = False
                            break
                    
                    if can_place:
                        # Place lab in both slots
                        original_code = session.get('original_code', subject_code)
                        for slot in slot_group:
                            timetable[day][slot] = {
                                'subject_code': original_code,
                                'subject_name': f"{original_code} Lab",
                                'faculty_name': faculty,
                                'section': section,
                                'room': f"Lab-{random.randint(1,10)}",
                                'type': 'lab'
                            }
                        daily_subjects[day].add(subject_code)
                        daily_labs[day].add(subject_code)
                        section_daily_labs[day] = True
                        return True
            return False
        else:
            # Place theory classes - avoid last period when possible
            available_slots = []
            for day in self.days:
                # Skip if subject already scheduled on this day
                if subject_code in daily_subjects[day]:
                    continue
                    
                # Try each time slot (avoid last period initially)
                for slot in range(5):  # 0-4, avoiding slot 5 (last period)
                    if timetable[day][slot] is None:
                        if not self.check_faculty_conflict(faculty, day, slot, existing_timetables):
                            if not self.check_department_conflict(target_dept, day, slot, existing_timetables):
                                available_slots.append((day, slot))
            
            # If no slots available in first 5 periods, try last period
            if not available_slots:
                for day in self.days:
                    if subject_code in daily_subjects[day]:
                        continue
                    slot = 5  # Last period
                    if timetable[day][slot] is None:
                        if not self.check_faculty_conflict(faculty, day, slot, existing_timetables):
                            if not self.check_department_conflict(target_dept, day, slot, existing_timetables):
                                available_slots.append((day, slot))
            
            if available_slots:
                day, slot = random.choice(available_slots)
                timetable[day][slot] = {
                    'subject_code': subject_code,
                    'subject_name': subject_code,
                    'faculty_name': faculty,
                    'section': section,
                    'room': f"Room-{random.randint(101,140)}",
                    'type': 'theory'
                }
                daily_subjects[day].add(subject_code)
                return True
            return False

    def _force_place_session(self, timetable: Dict[str, Dict[int, Optional[Dict[str, Any]]]],
                             session: Dict[str, Any], section: str) -> None:
        subj = session.get('subject_code')
        fac = session.get('faculty_name')
        typ = (session.get('type') or 'theory').lower()
        for day in self.days:
            if typ == 'lab':
                for group in self.continuous_slots:
                    # Check if we can replace FREE periods or force place
                    can_place = True
                    for s in group:
                        entry = timetable[day][s]
                        if entry and entry.get('type') != 'free':
                            can_place = False
                            break
                    if can_place:
                        original_code = session.get('original_code', subj)
                        for s in group:
                            timetable[day][s] = {
                                'subject_code': original_code,
                                'subject_name': f"{original_code} Lab",
                                'faculty_name': fac,
                                'section': section,
                                'room': f"Lab-{random.randint(1,10)}",
                                'type': 'lab'
                            }
                        return
            else:
                # Try to place in non-last periods first
                for s in range(5):
                    entry = timetable[day][s]
                    if entry is None or entry.get('type') == 'free':
                        timetable[day][s] = {
                            'subject_code': subj,
                            'subject_name': subj,
                            'faculty_name': fac,
                            'section': section,
                            'room': f"Room-{random.randint(101,140)}",
                            'type': 'theory'
                        }
                        return
                # If no space in first 5 periods, use last period
                entry = timetable[day][5]
                if entry is None or entry.get('type') == 'free':
                    timetable[day][5] = {
                        'subject_code': subj,
                        'subject_name': subj,
                        'faculty_name': fac,
                        'section': section,
                        'room': f"Room-{random.randint(101,140)}",
                        'type': 'theory'
                    }
                    return

    def calculate_fitness(self, timetable: Dict[str, Dict[int, Optional[Dict[str, Any]]]]) -> int:
        score = 0
        for day in self.days:
            for s in range(6):
                if timetable[day].get(s):
                    score += 1
        return score

    def validate_timetable(self, timetable: Dict[str, Dict[int, Optional[Dict[str, Any]]]]) -> Dict[str, Any]:
        conflicts: List[Dict[str, Any]] = []
        faculty_map: Dict[tuple, Dict[str, Any]] = {}
        section_map: Dict[tuple, Dict[str, Any]] = {}
        room_map: Dict[tuple, Dict[str, Any]] = {}

        for day in self.days:
            for s in range(6):
                e = timetable[day].get(s)
                if not e:
                    continue
                fac = e.get('faculty_name')
                sect = e.get('section')
                rm = e.get('room')
                key_fac = (fac, day, s)
                key_sec = (sect, day, s)
                key_room = (rm, day, s)
                if fac:
                    if key_fac in faculty_map:
                        conflicts.append({'type': 'faculty_double', 'faculty': fac, 'day': day, 'slot': s, 'entries': [faculty_map[key_fac], e]})
                    else:
                        faculty_map[key_fac] = e
                if sect:
                    if key_sec in section_map:
                        conflicts.append({'type': 'student_double', 'section': sect, 'day': day, 'slot': s, 'entries': [section_map[key_sec], e]})
                    else:
                        section_map[key_sec] = e
                if rm:
                    if key_room in room_map:
                        conflicts.append({'type': 'room_double', 'room': rm, 'day': day, 'slot': s, 'entries': [room_map[key_room], e]})
                    else:
                        room_map[key_room] = e

        for day in self.days:
            for group in self.continuous_slots:
                a = timetable[day].get(group[0])
                b = timetable[day].get(group[1])
                if (a and a.get('type') == 'lab') or (b and b.get('type') == 'lab'):
                    if not a or not b or a.get('subject_code') != b.get('subject_code'):
                        conflicts.append({'type': 'lab_continuity', 'day': day, 'slots': group, 'entries': [a, b]})

        for day in self.days:
            seen = {}
            for s in range(6):
                e = timetable[day].get(s)
                if not e:
                    continue
                subj = e.get('subject_code')
                sect = e.get('section')
                key = (sect, subj)
                if key in seen:
                    conflicts.append({'type': 'subject_repeat_same_day', 'section': sect, 'subject': subj, 'day': day, 'first_slot': seen[key], 'second_slot': s})
                else:
                    seen[key] = s

        return {'valid': len(conflicts) == 0, 'conflicts': conflicts}

    def find_swap_suggestions(self, timetable: Dict[str, Dict[int, Optional[Dict[str, Any]]]],
                              conflict: Dict[str, Any], existing_timetables: List[Dict[str, Any]],
                              max_suggestions: int = 5) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []
        entries = conflict.get('entries') or []
        if not entries:
            return suggestions
        victim = entries[-1]
        subj = victim.get('subject_code')
        fac = victim.get('faculty_name')
        typ = victim.get('type')

        def slot_is_free(day: str, slot: int) -> bool:
            if timetable[day].get(slot) is not None:
                return False
            if self.check_faculty_conflict(fac, day, slot, existing_timetables):
                return False
            return True

        for day in self.days:
            if len(suggestions) >= max_suggestions:
                break
            for s in range(6):
                if typ == 'lab':
                    for group in self.continuous_slots:
                        if group[0] != s:
                            continue
                        if all(timetable[day].get(g) is None for g in group) and all(not self.check_faculty_conflict(fac, day, g, existing_timetables) for g in group):
                            suggestions.append({'day': day, 'slots': group, 'reason': 'same_day_continuous'})
                            if len(suggestions) >= max_suggestions:
                                break
                else:
                    if slot_is_free(day, s):
                        suggestions.append({'day': day, 'slot': s, 'reason': 'same_day_free'})
                        if len(suggestions) >= max_suggestions:
                            break

        for day in self.days:
            if len(suggestions) >= max_suggestions:
                break
            for s in range(6):
                if typ == 'lab':
                    for group in self.continuous_slots:
                        if all(timetable[day].get(g) is None for g in group) and all(not self.check_faculty_conflict(fac, day, g, existing_timetables) for g in group):
                            suggestions.append({'day': day, 'slots': group, 'reason': 'other_day_continuous'})
                            if len(suggestions) >= max_suggestions:
                                break
                else:
                    if slot_is_free(day, s):
                        suggestions.append({'day': day, 'slot': s, 'reason': 'other_day_free'})
                        if len(suggestions) >= max_suggestions:
                            break

        return suggestions[:max_suggestions]

    def evolve_section(self, department: str, section: str, section_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        assignments: List[Dict[str, Any]] = []
        for a in section_data:
            subj = a.get('subject') or a.get('sub_code') or a.get('subject_code')
            fac = a.get('faculty') or a.get('faculty_name') or a.get('facultyName')
            target_dept = a.get('target_department') or a.get('targetDept') or department
            if subj:
                assignments.append({'subject_code': subj, 'faculty_name': fac, 'target_department': target_dept})

        subjects_db, faculty_db, existing_timetables = self.fetch_data(department=department, section=section)

        subject_keys = [x['subject_code'] for x in assignments if x.get('subject_code')]
        subject_hours = self.get_subject_hours_from_db(department, subject_keys)

        lab_sessions: List[Dict[str, Any]] = []
        theory_sessions: List[Dict[str, Any]] = []
        
        # Process each assignment and create sessions based on weekly hours and type
        for a in assignments:
            code = a['subject_code']
            fac = a.get('faculty_name')
            info = subject_hours.get(code, {'weekly_hours': 3, 'type': 'theory'})
            hours = int(info.get('weekly_hours', 3))
            typ = info.get('type', 'theory').lower()
            
            if typ == 'lab':
                # Labs are 2-hour continuous sessions - distribute across different days
                if hours == 4:
                    # 4-hour lab = 2 separate 2-hour sessions on different days
                    for i in range(2):
                        lab_sessions.append({
                            'subject_code': f"{code}_L{i+1}",  # Unique identifier for each lab session
                            'original_code': code,
                            'faculty_name': fac, 
                            'type': 'lab', 
                            'target_department': a['target_department']
                        })
                elif hours >= 2:
                    # 2-hour or 3-hour lab = 1 session (2 continuous periods)
                    lab_sessions.append({
                        'subject_code': code, 
                        'faculty_name': fac, 
                        'type': 'lab', 
                        'target_department': a['target_department']
                    })
            else:
                # Theory classes - one session per weekly hour
                for _ in range(hours):
                    theory_sessions.append({
                        'subject_code': code, 
                        'faculty_name': fac, 
                        'type': 'theory', 
                        'target_department': a['target_department']
                    })

        # Initialize empty timetable
        timetable: Dict[str, Dict[int, Optional[Dict[str, Any]]]] = {d: {s: None for s in range(6)} for d in self.days}
        daily_subjects = {d: set() for d in self.days}
        daily_labs = {d: set() for d in self.days}
        section_daily_labs = {d: False for d in self.days}  # Track if section has lab on each day

        # Shuffle lab sessions to distribute across different days
        random.shuffle(lab_sessions)
        
        # Place labs first (higher priority)
        for session in lab_sessions:
            placed = self._place_session_with_constraints(timetable, session, daily_subjects, daily_labs, section_daily_labs, existing_timetables, section)
            if not placed:
                print(f"Warning: Could not place lab {session['subject_code']} optimally, forcing placement")
                self._force_place_session(timetable, session, section)

        # Place theory sessions
        for session in theory_sessions:
            placed = self._place_session_with_constraints(timetable, session, daily_subjects, daily_labs, section_daily_labs, existing_timetables, section)
            if not placed:
                print(f"Warning: Could not place theory {session['subject_code']} optimally, forcing placement")
                self._force_place_session(timetable, session, section)
        
        # Fill remaining slots with FREE periods (prioritize last period)
        for day in self.days:
            # First try to place FREE in last period (slot 5)
            if timetable[day][5] is None:
                timetable[day][5] = {
                    'subject_code': 'FREE',
                    'subject_name': 'Free Period',
                    'faculty_name': 'N/A',
                    'section': section,
                    'room': 'N/A',
                    'type': 'free'
                }
            # Then fill other empty slots with FREE
            for slot in range(5):
                if timetable[day][slot] is None:
                    timetable[day][slot] = {
                        'subject_code': 'FREE',
                        'subject_name': 'Free Period',
                        'faculty_name': 'N/A',
                        'section': section,
                        'room': 'N/A',
                        'type': 'free'
                    }

        # Validate the final timetable
        validation = self.validate_timetable(timetable)
        if not validation.get('valid', False):
            print(f"Timetable validation failed for {department} {section}")
            for conf in validation.get('conflicts', []):
                conf['suggestions'] = self.find_swap_suggestions(timetable, conf, existing_timetables)
            validation['timetable'] = timetable
            return validation

        print(f"Successfully generated valid timetable for {department} {section}")
        return {'valid': True, 'timetable': timetable}

    def save_to_supabase(self, timetable: Dict[str, Dict[int, Any]], section: str, department: str,
                         academic_year: Optional[str] = None, year: Optional[int] = None, semester: Optional[int] = None) -> None:
        rows: List[Dict[str, Any]] = []
        processed_labs = set()
        
        for day in self.days:
            for s in range(6):
                e = timetable[day].get(s)
                if not e:
                    continue
                
                # For labs, only save the first slot of the pair
                if e.get('type') == 'lab':
                    lab_key = f"{day}-{e.get('subject_code')}-{section}"
                    if lab_key in processed_labs:
                        continue  # Skip second slot of lab
                    processed_labs.add(lab_key)
                
                rows.append({
                    'department': department,
                    'section': section,
                    'day': day,
                    'time_slot': s,
                    'subject_code': e.get('subject_code'),
                    'subject_name': e.get('subject_name'),
                    'faculty_name': e.get('faculty_name'),
                    'room': e.get('room'),
                    'type': e.get('type'),
                    'academic_year': academic_year,
                    'year': year,
                    'semester': semester
                })
        try:
            del_q = self.supabase.table('timetables').delete().eq('department', department).eq('section', section)
            if academic_year:
                del_q = del_q.eq('academic_year', academic_year)
            if year is not None:
                del_q = del_q.eq('year', int(year))
            if semester is not None:
                del_q = del_q.eq('semester', int(semester))
            del_q.execute()
            if rows:
                self.supabase.table('timetables').insert(rows).execute()
        except Exception as e:
            print(f"save_to_supabase error: {e}", file=sys.stderr)