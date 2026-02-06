# 🎓 MIT Mysore Timetable System - Improved Version

## 🚀 Recent Improvements

### ✅ Lab Scheduling Fixes
- **Labs are now scheduled on different days** - No two labs will be on the same day
- **Improved conflict detection** - Better handling of faculty and room conflicts
- **Enhanced lab display** - Labs show as 2-hour continuous blocks with proper styling

### ✅ UI/UX Improvements
- **Fixed button overlapping** - All control buttons now have proper spacing and don't overlap
- **Enhanced subject details table** - Shows comprehensive information including:
  - Subject codes and names
  - Faculty names with initials
  - Subject types (Theory/Lab) with icons
  - Credits and department information
  - Summary statistics
- **Better visual styling** - Improved colors, icons, and layout

### ✅ Enhanced Features
- **Smart section navigation** - Better navigation between multiple sections
- **Improved timetable display** - Better visual distinction between theory and lab classes
- **Enhanced subject details** - More comprehensive information display

## 🛠️ How to Run the System

### Step 1: Install Dependencies
```bash
cd "C:\Users\surav\Downloads\TimeTable-Python\TimeTable-f4ae7f0d5f107ac07b8e7e3c093e277ee7f78ddf"
pip install flask==3.0.0 flask-cors==4.0.0 supabase==2.3.0 requests==2.31.0 python-dotenv==1.0.0
```

### Step 2: Test the System
```bash
python test_server.py
```

### Step 3: Start the Flask Server
```bash
python flask_server.py
```

**OR** use the batch file:
```bash
START_SYSTEM.bat
```

### Step 4: Access the System
Open your web browser and go to:
- **Main Interface**: http://127.0.0.1:5000/timetable-new.htm
- **Dashboard**: http://127.0.0.1:5000/dashboard.htm

## 📋 System Features

### 🧬 Genetic Algorithm Improvements
- **Lab Constraint**: Labs are automatically placed on different days
- **Conflict Detection**: Advanced faculty and room conflict checking
- **Random Placement**: Ensures variety in timetable generation
- **30-Period Fill**: Guarantees all 30 periods are filled (5 days × 6 periods)

### 🎨 UI Improvements
- **Responsive Design**: Better layout that works on different screen sizes
- **Visual Indicators**: Icons for different subject types (📚 Theory, 🧪 Lab, 🆓 Free)
- **Color Coding**: Different colors for different subject types
- **Hover Effects**: Interactive elements with smooth transitions

### 📊 Enhanced Subject Details
The subject details table now shows:
- **Subject Code**: Unique identifier for each subject
- **Subject Name**: Full name of the subject
- **Type**: Theory or Lab with appropriate icons
- **Credits**: Number of credits for the subject
- **Faculty Name**: Full name of assigned faculty
- **Faculty Initials**: Easy-to-read initials
- **Department**: Faculty department information
- **Summary Statistics**: Quick overview of the timetable

### 🔄 Smart Swap Feature
- **Conflict Detection**: Checks for faculty conflicts before swapping
- **Visual Feedback**: Clear indication of swappable classes
- **Intelligent Suggestions**: Provides alternative time slots if conflicts exist

## 🎯 Key Improvements Made

### 1. Lab Scheduling Algorithm
```python
# Before: Labs could be on the same day
# After: Labs are forced to different days
days_with_labs = set()
for lab in labs:
    for day in available_lab_days:
        if day in days_with_labs:
            continue  # Skip days that already have labs
```

### 2. Button Layout Fix
```css
/* Before: Buttons could overlap */
.controls {
    gap: 10px;
    min-width: 160px;
}

/* After: Proper spacing and sizing */
.controls {
    gap: 8px;
    max-width: 200px;
}
.control-btn {
    min-width: 140px;
    max-width: 180px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
```

### 3. Enhanced Subject Details
```javascript
// Before: Basic subject info
// After: Comprehensive details with styling
tableHTML += `
    <td style="background: ${typeColor}; font-weight: bold;">
        ${typeBadge} ${displayType}
    </td>
    <td style="background: #fff3cd; font-family: monospace;">
        ${displayFacultyInitials}
    </td>
`;
```

## 🔧 Troubleshooting

### Common Issues:

1. **Server won't start**
   - Check if all dependencies are installed: `pip list`
   - Verify Python version: `python --version` (should be 3.7+)

2. **Database connection issues**
   - Check internet connection
   - Verify Supabase credentials in the code

3. **Timetable generation fails**
   - Ensure all subjects have assigned faculty
   - Check for conflicting schedules

4. **Buttons overlapping**
   - Clear browser cache and refresh
   - Check if CSS is loading properly

## 📱 Browser Compatibility
- ✅ Chrome (Recommended)
- ✅ Firefox
- ✅ Edge
- ⚠️ Safari (Limited testing)

## 🎉 Success Indicators

When the system is working correctly, you should see:
- ✅ Labs scheduled on different days
- ✅ All 30 time slots filled
- ✅ No button overlapping
- ✅ Comprehensive subject details table
- ✅ Proper visual styling with icons

## 📞 Support

If you encounter any issues:
1. Check the browser console for errors (F12)
2. Verify the Flask server is running
3. Test with the provided `test_server.py` script
4. Check the terminal/command prompt for error messages

---

**🎓 MIT Mysore Timetable System - Enhanced for Better User Experience!**