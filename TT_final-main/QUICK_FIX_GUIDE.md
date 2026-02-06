# 🚀 QUICK FIX - Timetable Generation Error

## ❌ **Error 405 - Cannot Connect to Backend Server**

### **SOLUTION:**

#### **Step 1: Start the Flask Server**
```bash
# Option 1: Double-click this file
START_SERVER.bat

# Option 2: Open Command Prompt and run:
cd "C:\Users\surav\Downloads\TimeTable-Python\TimeTable-f4ae7f0d5f107ac07b8e7e3c093e277ee7f78ddf"
python flask_server.py
```

#### **Step 2: Wait for Server to Start**
You should see:
```
Starting MIT Mysore Timetable Server (Enhanced)...
Server running on http://localhost:5000
```

#### **Step 3: Test the Connection**
Open browser and go to: `http://localhost:5000/health`
You should see: `{"status": "ok"}`

#### **Step 4: Now Generate Timetable**
Go back to your timetable page and click "Generate Timetable"

---

## 🔧 **If Still Not Working:**

### **Check Python Dependencies:**
```bash
pip install flask flask-cors supabase
```

### **Check if Port 5000 is Free:**
```bash
netstat -ano | findstr :5000
```

### **Alternative Port (if 5000 is busy):**
Edit `flask_server.py` line 500+:
```python
app.run(debug=True, port=5001, host='0.0.0.0')
```

Then update `timetable-new.htm` URLs from `:5000` to `:5001`

---

## ✅ **Quick Test:**

1. **Start Server**: Run `START_SERVER.bat`
2. **Check Health**: Visit `http://localhost:5000/health`
3. **Generate**: Try timetable generation again

**The server MUST be running for timetable generation to work!**