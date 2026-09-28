#!/usr/bin/env python3
"""
Test script to generate a sample report and show the improved timestamp visibility.
Uses fictional placeholder data only (no real patient/facility PHI).
"""

import sys
import os
sys.path.append('src')

from report_generator import generate_execution_report

def test_timestamp_visibility():
    """Generate a sample report to test timestamp visibility"""
    
    # Fictional sample data only
    sample_data = {
        'facility_name': 'Example Clinic (Demo)',
        'total_patients': 5,
        'processed_patients': 4,
        'skipped_patients': 1,
        'total_files_downloaded': 25,
        'patients': [
            {
                'patient_id': '100001',
                'patient_name': 'Jane Example',
                'status': 'Completed',
                'encounters': 2,
                'consent_forms': 1,
                'invoices': 3,
                'images': 2,
                'membership_invoices': 1,
                'total_files': 9
            },
            {
                'patient_id': '100002',
                'patient_name': 'John Sample',
                'status': 'Completed',
                'encounters': 1,
                'consent_forms': 2,
                'invoices': 2,
                'images': 1,
                'membership_invoices': 0,
                'total_files': 6
            }
        ]
    }
    
    # Create reports directory
    reports_dir = os.path.join('downloads', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate test report
    report_filename = "Timestamp_Visibility_Test_Report.html"
    report_path = generate_execution_report(sample_data, reports_dir, report_filename)
    
    print("✅ Test report generated successfully!")
    print(f"📄 Report location: {report_path}")
    print("\n🔍 Timestamp Improvements:")
    print("• Enhanced visibility with blue color (#2563eb)")
    print("• Larger font size (1.1em)")
    print("• Bold font weight (600)")
    print("• Professional background gradient")
    print("• Rounded corners and subtle shadow")
    print("• Clock emoji (🕒) for visual appeal")
    print("• Centered alignment")
    print("• Better spacing and padding")
    
    return report_path

if __name__ == "__main__":
    test_timestamp_visibility()
