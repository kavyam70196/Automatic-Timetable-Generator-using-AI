// Debug script to check save functionality
console.log('=== SAVE DEBUG SCRIPT ===');

// Check if timetable data exists
const timetableData = JSON.parse(localStorage.getItem('timetableData') || '{}');
console.log('Timetable data:', timetableData);

// Check section containers
const containers = document.querySelectorAll('.timetable-section-container');
console.log(`Found ${containers.length} section containers`);

containers.forEach((container, index) => {
    const sectionName = container.id.replace('section-container-', '');
    console.log(`\nSection ${index + 1}: ${sectionName}`);
    
    const allCells = container.querySelectorAll('.subject-cell');
    const cellsWithData = container.querySelectorAll('.subject-cell[data-subject]');
    
    console.log(`  Total cells: ${allCells.length}`);
    console.log(`  Cells with data: ${cellsWithData.length}`);
    
    // Check first few cells
    allCells.forEach((cell, cellIndex) => {
        if (cellIndex < 6) { // Check first 6 cells
            const subject = cell.getAttribute('data-subject');
            const faculty = cell.getAttribute('data-faculty');
            const type = cell.getAttribute('data-type');
            const day = cell.dataset.day;
            const slot = cell.dataset.slot;
            
            console.log(`    Cell ${cellIndex + 1} (${day} P${slot}): ${subject || 'NO SUBJECT'} - ${faculty || 'NO FACULTY'} (${type || 'NO TYPE'})`);
        }
    });
});

// Test save data preparation
function testSavePreparation() {
    const newEntries = [];
    const sectionContainers = document.querySelectorAll('.timetable-section-container');
    
    sectionContainers.forEach(container => {
        const sectionName = container.id.replace('section-container-', '');
        
        container.querySelectorAll('.subject-cell').forEach(cell => {
            const subjectCode = cell.getAttribute('data-subject');
            const type = cell.getAttribute('data-type') || 'theory';
            const day = cell.dataset.day;
            const slot = parseInt(cell.dataset.slot);
            
            if (subjectCode && day && slot) {
                newEntries.push({
                    section: sectionName,
                    day: day,
                    time_slot: slot,
                    subject_code: subjectCode,
                    faculty_name: cell.getAttribute('data-faculty') || 'N/A',
                    type: type
                });
            }
        });
    });
    
    console.log(`\nPrepared ${newEntries.length} entries for saving:`);
    newEntries.slice(0, 5).forEach((entry, index) => {
        console.log(`  Entry ${index + 1}:`, entry);
    });
    
    return newEntries.length;
}

const entryCount = testSavePreparation();
console.log(`\n=== RESULT: ${entryCount} entries ready for save ===`);

if (entryCount === 0) {
    console.error('ERROR: No entries found! Check if timetable is properly loaded and cells have data attributes.');
} else {
    console.log('SUCCESS: Save data is ready!');
}