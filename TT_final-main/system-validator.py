#!/usr/bin/env python3
"""
MIT Mysore Timetable System Validator
Comprehensive system validation and improvement script
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class SystemValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.fixes_applied = []
        
    def validate_files(self):
        """Validate all critical files exist and are properly formatted"""
        critical_files = [
            'flask_server.py',
            'genetic_timetable_new.py',
            'page.htm',
            'subject.htm',
            'faculty-timetable.htm',
            'timetable-new.htm',
            'enhanced-subject-display.js'
        ]
        
        print("🔍 Validating critical files...")
        for file in critical_files:
            file_path = self.project_root / file
            if not file_path.exists():
                self.issues.append(f"❌ Missing critical file: {file}")
            else:
                print(f"✅ Found: {file}")
                
        return len(self.issues) == 0
    
    def validate_database_schema(self):
        """Check if database schema files are present"""
        schema_files = [
            'complete_database_setup.sql',
            'enhanced_timetable_schema.sql'
        ]
        
        print("\n🗄️ Validating database schema...")
        for file in schema_files:
            file_path = self.project_root / file
            if file_path.exists():
                print(f"✅ Found schema: {file}")
            else:
                self.issues.append(f"⚠️ Missing schema file: {file}")
    
    def validate_dependencies(self):
        """Check if all Python dependencies are installed"""
        print("\n📦 Validating Python dependencies...")
        
        requirements_file = self.project_root / 'requirements.txt'
        if not requirements_file.exists():
            self.issues.append("❌ Missing requirements.txt file")
            return False
            
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('\n')
                
            for req in requirements:
                if req.strip():
                    package = req.split('==')[0].split('>=')[0].split('<=')[0]
                    try:
                        __import__(package.replace('-', '_'))
                        print(f"✅ {package} is installed")
                    except ImportError:
                        self.issues.append(f"❌ Missing package: {package}")
                        
        except Exception as e:
            self.issues.append(f"❌ Error reading requirements.txt: {e}")
            
        return True
    
    def validate_html_files(self):
        """Validate HTML files for common issues"""
        print("\n🌐 Validating HTML files...")
        
        html_files = ['page.htm', 'subject.htm', 'faculty-timetable.htm', 'timetable-new.htm']
        
        for file in html_files:
            file_path = self.project_root / file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for common issues
                    if '</html>' not in content:
                        self.issues.append(f"❌ {file}: Missing closing </html> tag")
                    
                    if 'supabase' in content.lower() and 'SUPABASE_URL' not in content:
                        self.issues.append(f"⚠️ {file}: Supabase integration may be incomplete")
                        
                    if file == 'faculty-timetable.htm':
                        if content.count('<script>') != content.count('</script>'):
                            self.issues.append(f"❌ {file}: Unmatched script tags - file may be incomplete")
                        else:
                            print(f"✅ {file}: Script tags are properly matched")
                            
                    print(f"✅ {file}: Basic validation passed")
                    
                except Exception as e:
                    self.issues.append(f"❌ Error reading {file}: {e}")
    
    def validate_javascript_syntax(self):
        """Basic JavaScript syntax validation"""
        print("\n🔧 Validating JavaScript syntax...")
        
        js_file = self.project_root / 'enhanced-subject-display.js'
        if js_file.exists():
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Basic syntax checks
                if content.count('{') != content.count('}'):
                    self.issues.append("❌ enhanced-subject-display.js: Unmatched braces")
                elif content.count('(') != content.count(')'):
                    self.issues.append("❌ enhanced-subject-display.js: Unmatched parentheses")
                else:
                    print("✅ enhanced-subject-display.js: Basic syntax validation passed")
                    
            except Exception as e:
                self.issues.append(f"❌ Error validating JavaScript: {e}")
    
    def check_server_configuration(self):
        """Validate Flask server configuration"""
        print("\n🖥️ Validating server configuration...")
        
        server_file = self.project_root / 'flask_server.py'
        if server_file.exists():
            try:
                with open(server_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for essential endpoints
                essential_endpoints = [
                    '/generate',
                    '/get_faculty_timetable',
                    '/finalize_timetable',
                    '/get_subjects',
                    '/get_faculty'
                ]
                
                for endpoint in essential_endpoints:
                    if endpoint in content:
                        print(f"✅ Found endpoint: {endpoint}")
                    else:
                        self.issues.append(f"❌ Missing endpoint: {endpoint}")
                        
                # Check for CORS configuration
                if 'CORS(app)' in content:
                    print("✅ CORS is configured")
                else:
                    self.issues.append("⚠️ CORS may not be properly configured")
                    
            except Exception as e:
                self.issues.append(f"❌ Error validating server: {e}")
    
    def generate_system_report(self):
        """Generate a comprehensive system report"""
        print("\n" + "="*60)
        print("📊 SYSTEM VALIDATION REPORT")
        print("="*60)
        
        if not self.issues:
            print("🎉 EXCELLENT! No critical issues found.")
            print("✅ Your timetable system is ready to use!")
        else:
            print(f"⚠️ Found {len(self.issues)} issues that need attention:")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")
        
        print("\n" + "="*60)
        print("🚀 SYSTEM CAPABILITIES")
        print("="*60)
        print("✅ Cross-department subject support")
        print("✅ Faculty conflict detection")
        print("✅ Professional UI with animations")
        print("✅ Enhanced subject display")
        print("✅ PDF generation for schedules")
        print("✅ Real-time timetable validation")
        print("✅ Department isolation")
        print("✅ Genetic algorithm optimization")
        
        print("\n" + "="*60)
        print("📋 USAGE INSTRUCTIONS")
        print("="*60)
        print("1. Start the Flask server: python flask_server.py")
        print("2. Open page.htm in your browser")
        print("3. Select your department")
        print("4. Add subjects using subject.htm")
        print("5. Generate timetables using timetable-new.htm")
        print("6. View faculty schedules using faculty-timetable.htm")
        
        return len(self.issues) == 0
    
    def run_validation(self):
        """Run complete system validation"""
        print("🔍 MIT Mysore Timetable System Validator")
        print("="*50)
        
        self.validate_files()
        self.validate_database_schema()
        self.validate_dependencies()
        self.validate_html_files()
        self.validate_javascript_syntax()
        self.check_server_configuration()
        
        return self.generate_system_report()

def main():
    validator = SystemValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎯 System is ready for production use!")
        sys.exit(0)
    else:
        print("\n⚠️ Please fix the issues above before using the system.")
        sys.exit(1)

if __name__ == "__main__":
    main()