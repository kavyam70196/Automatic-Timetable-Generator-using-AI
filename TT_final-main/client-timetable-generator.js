// Client-Side Timetable Generator
// No Flask server required - works directly in browser

class ClientTimetableGenerator {
    constructor() {
        this.days = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        this.timeSlots = [
            { id: 1, name: 'Period 1', time: '09:00 - 10:00' },
            { id: 2, name: 'Period 2', time: '10:00 - 11:00' },
            { id: 3, name: 'Period 3', time: '11:15 - 12:15' },
            { id: 4, name: 'Period 4', time: '12:15 - 13:15' },
            { id: 5, name: 'Period 5', time: '14:00 - 15:00' },
            { id: 6, name: 'Period 6', time: '15:00 - 16:00' }
        ];
        this.labSlots = [[1, 2], [3, 4], [5, 6]]; // Consecutive periods for labs
    }

    generateTimetable(sections) {
        const results = {};
        
        for (const section of sections) {
            try {
                const timetable = this.generateSectionTimetable(section);
                results[section.name] = {
                    valid: true,
                    timetable: timetable,
                    section_name: section.name
                };
            } catch (error) {
                results[section.name] = {
                    valid: false,
                    error: error.message
                };
            }
        }
        
        return results;
    }

    generateSectionTimetable(section) {
        const timetable = {};
        
        // Initialize empty timetable
        this.days.forEach(day => {
            timetable[day] = {};
            this.timeSlots.forEach(slot => {
                timetable[day][slot.id] = null;
            });
        });

        // Process assignments
        const sessions = this.createSessions(section.assignments);
        
        // Place sessions in timetable
        this.placeSessions(timetable, sessions, section.name);
        
        return timetable;
    }

    createSessions(assignments) {
        const sessions = [];
        
        assignments.forEach(assignment => {
            const weeklyHours = assignment.weekly_hours || 3;
            const type = assignment.type || 'theory';
            
            if (type === 'lab') {
                // Labs take 2 consecutive periods
                const labSessions = Math.floor(weeklyHours / 2);
                for (let i = 0; i < labSessions; i++) {
                    sessions.push({
                        ...assignment,
                        type: 'lab',
                        periods: 2
                    });
                }
                // Remaining hours as theory
                const remainingHours = weeklyHours % 2;
                for (let i = 0; i < remainingHours; i++) {
                    sessions.push({
                        ...assignment,
                        type: 'theory',
                        periods: 1
                    });
                }
            } else {
                // Theory/Free subjects - one period each
                for (let i = 0; i < weeklyHours; i++) {
                    sessions.push({
                        ...assignment,
                        type: type,
                        periods: 1
                    });
                }
            }
        });

        return sessions;
    }

    placeSessions(timetable, sessions, sectionName) {
        // Shuffle sessions for randomization
        const shuffledSessions = [...sessions].sort(() => Math.random() - 0.5);
        
        // Place lab sessions first (need consecutive slots)
        const labSessions = shuffledSessions.filter(s => s.type === 'lab');
        const otherSessions = shuffledSessions.filter(s => s.type !== 'lab');
        
        // Place labs
        labSessions.forEach(session => {
            this.placeLabSession(timetable, session, sectionName);
        });
        
        // Place other sessions
        otherSessions.forEach(session => {
            this.placeRegularSession(timetable, session, sectionName);
        });
    }

    placeLabSession(timetable, session, sectionName) {
        let availableSlots = [];
        
        // Find available consecutive slots
        this.days.forEach(day => {
            this.labSlots.forEach(slotPair => {
                if (timetable[day][slotPair[0]] === null && timetable[day][slotPair[1]] === null) {
                    availableSlots.push({ day, slots: slotPair });
                }
            });
        });
        
        // Filter out days where this lab subject already exists
        availableSlots = availableSlots.filter(slot => {
            const subjectsOnDay = Object.values(timetable[slot.day]).map(e => e ? (e.subject_code || e.subject) : null);
            return !subjectsOnDay.includes(session.subject_code || session.subject);
        });
        
        if (availableSlots.length > 0) {
            const chosen = availableSlots[Math.floor(Math.random() * availableSlots.length)];
            const room = `Lab-${Math.floor(Math.random() * 10) + 1}`;
            
            chosen.slots.forEach(slot => {
                timetable[chosen.day][slot] = {
                    subject_code: session.subject_code || session.subject,
                    subject_name: session.subject,
                    faculty_name: session.faculty,
                    section: sectionName,
                    room: room,
                    type: 'lab',
                    is_cross_dept: session.is_cross_dept || false,
                    teaching_dept: session.teaching_dept
                };
            });
        }
    }

    placeRegularSession(timetable, session, sectionName) {
        let availableSlots = [];
        
        // Find available single slots
        this.days.forEach(day => {
            this.timeSlots.forEach(slot => {
                if (timetable[day][slot.id] === null) {
                    availableSlots.push({ day, slot: slot.id });
                }
            });
        });

        // Filter available slots based on constraints
        if (session.type === 'theory') {
            availableSlots = availableSlots.filter(slot => {
                const subjectsOnDay = Object.values(timetable[slot.day]).map(e => e ? (e.subject_code || e.subject) : null);
                return !subjectsOnDay.includes(session.subject_code || session.subject);
            });
        }

        // Special rule for 'free' periods - only in P6
        if (session.type === 'free') {
            availableSlots = availableSlots.filter(s => s.slot === 6);
        }
        
        if (availableSlots.length > 0) {
            const chosen = availableSlots[Math.floor(Math.random() * availableSlots.length)];
            const room = `Room-${sectionName}01`;
            
            timetable[chosen.day][chosen.slot] = {
                subject_code: session.subject_code || session.subject,
                subject_name: session.subject,
                faculty_name: session.faculty,
                section: sectionName,
                room: room,
                type: session.type,
                is_cross_dept: session.is_cross_dept || false,
                teaching_dept: session.teaching_dept
            };
        }
    }

    fillFreeSlots(timetable) {
        this.days.forEach(day => {
            this.timeSlots.forEach(slot => {
                if (timetable[day][slot.id] === null) {
                    timetable[day][slot.id] = {
                        subject_code: 'FREE',
                        subject_name: 'Free Period',
                        faculty_name: 'N/A',
                        section: '',
                        room: '',
                        type: 'free'
                    };
                }
            });
        });
    }
}

// Replace the Flask server call with client-side generation
async function callClientTimetableGenerator(inputData) {
    return new Promise((resolve) => {
        setTimeout(() => {
            const generator = new ClientTimetableGenerator();
            const results = generator.generateTimetable(inputData.sections);
            resolve(results);
        }, 1000); // Simulate processing time
    });
}