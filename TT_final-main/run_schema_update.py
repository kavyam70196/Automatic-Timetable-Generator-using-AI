#!/usr/bin/env python3
"""
Script to update database schema for Tuesday-Saturday schedule
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase._sync.client import create_client
except ImportError:
    try:
        from supabase.client import create_client
    except ImportError:
        from supabase import create_client

def update_database_schema():
    """Update database to support Tuesday-Saturday schedule"""
    
    SUPABASE_URL = "https://bkmzyhroignpjebfpqug.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrbXp5aHJvaWducGplYmZwcXVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc0MjA1NDUsImV4cCI6MjA3Mjk5NjU0NX0.ICE2eYzFZvz0dtNpAa5YlJTZD-idc2J76wn1ZeHwwck"
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # SQL to update day constraint
    update_sql = """
    -- Drop existing day constraint if it exists
    DO $$ 
    BEGIN
        -- Remove old day constraint
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name LIKE '%day%' 
            AND table_name = 'timetables'
        ) THEN
            ALTER TABLE timetables DROP CONSTRAINT IF EXISTS timetables_day_check;
        END IF;
    END $$;

    -- Add new day constraint for Tuesday-Saturday
    ALTER TABLE timetables ADD CONSTRAINT timetables_day_check 
        CHECK (day IN ('Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'));

    -- Update any existing Monday entries to Tuesday (if any)
    UPDATE timetables SET day = 'Tuesday' WHERE day = 'Monday';
    """
    
    try:
        print("Updating database schema for Tuesday-Saturday schedule...")
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': update_sql}).execute()
        
        print("SUCCESS: Database schema updated successfully!")
        print("Timetables now support Tuesday-Saturday schedule")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update schema: {e}")
        
        # Try alternative approach - direct SQL execution
        try:
            print("Trying alternative approach...")
            
            # Drop constraint
            drop_result = supabase.rpc('exec_sql', {
                'sql': 'ALTER TABLE timetables DROP CONSTRAINT IF EXISTS timetables_day_check;'
            }).execute()
            
            # Add new constraint
            add_result = supabase.rpc('exec_sql', {
                'sql': "ALTER TABLE timetables ADD CONSTRAINT timetables_day_check CHECK (day IN ('Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'));"
            }).execute()
            
            print("SUCCESS: Schema updated using alternative method!")
            return True
            
        except Exception as e2:
            print(f"ERROR: Alternative approach also failed: {e2}")
            print("Please run the SQL manually in Supabase SQL Editor:")
            print(update_sql)
            return False

if __name__ == "__main__":
    success = update_database_schema()
    sys.exit(0 if success else 1)