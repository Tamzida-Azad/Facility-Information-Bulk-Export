#!/usr/bin/env python3
"""
Standalone Report Generator Test
Generates a sample HTML report to test the report functionality independently.
Uses fictional placeholder data only (no real patient/facility PHI).
"""

import os
import sys
sys.path.append('src')

from report_generator import generate_execution_report

def main():
    """Generate a test report with sample data."""
    
    print("🔄 Generating test EMR export report...")
    
    # Fictional sample data only
    test_data = {
        'facility_name': 'Example Clinic (Demo)',
        'total_patients': 8,
        'processed_patients': 7,
        'skipped_patients': 1,
        'total_files_downloaded': 47,
        'patients': [
            {
                'patient_id': '100001',
                'patient_name': 'Jane Example',
                'status': 'Completed',
                'encounters': 3,
                'consent_forms': 2,
                'invoices': 2,
                'images': 7,
                'membership_invoices': 1,
                'total_files': 15
            },
            {
                'patient_id': '100002',
                'patient_name': 'John Sample',
                'status': 'Completed',
                'encounters': 2,
                'consent_forms': 1,
                'invoices': 3,
                'images': 4,
                'membership_invoices': 0,
                'total_files': 10
            },
            {
                'patient_id': '100003',
                'patient_name': 'Alex Demo',
                'status': 'Completed',
                'encounters': 1,
                'consent_forms': 2,
                'invoices': 1,
                'images': 5,
                'membership_invoices': 1,
                'total_files': 10
            },
            {
                'patient_id': '100004',
                'patient_name': 'Sam Placeholder',
                'status': 'Completed',
                'encounters': 2,
                'consent_forms': 1,
                'invoices': 2,
                'images': 2,
                'membership_invoices': 0,
                'total_files': 7
            },
            {
                'patient_id': '100005',
                'patient_name': 'Casey Test',
                'status': 'Completed',
                'encounters': 1,
                'consent_forms': 0,
                'invoices': 1,
                'images': 1,
                'membership_invoices': 0,
                'total_files': 3
            },
            {
                'patient_id': '100006',
                'patient_name': 'Riley Fiction',
                'status': 'Failed',
                'encounters': 0,
                'consent_forms': 0,
                'invoices': 0,
                'images': 0,
                'membership_invoices': 0,
                'total_files': 0
            },
            {
                'patient_id': '100007',
                'patient_name': 'Morgan Sample',
                'status': 'Completed',
                'encounters': 1,
                'consent_forms': 1,
                'invoices': 0,
                'images': 1,
                'membership_invoices': 0,
                'total_files': 3
            },
            {
                'patient_id': '100008',
                'patient_name': 'Taylor Dummy',
                'status': 'Completed',
                'encounters': 0,
                'consent_forms': 0,
                'invoices': 0,
                'images': 0,
                'membership_invoices': 0,
                'total_files': 0
            }
        ]
    }
    
    # Create reports directory
    reports_dir = os.path.join('downloads', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate report
    report_filename = "Test_EMR_Export_Report_04-30-2026.html"
    
    try:
        report_path = generate_execution_report(test_data, reports_dir, report_filename)
        
        print("✅ SUCCESS!")
        print(f"📄 Report generated: {report_path}")
        print("\n📊 Report Summary:")
        print(f"   • Total Patients: {test_data['total_patients']}")
        print(f"   • Processed: {test_data['processed_patients']}")
        print(f"   • Skipped: {test_data['skipped_patients']}")
        print(f"   • Total Files: {test_data['total_files_downloaded']}")
        print(f"   • Facility: {test_data['facility_name']}")
        
        print("\n🔍 Report Features:")
        print("   ✓ Document Type Statistics (all 5 types)")
        print("   ✓ Patient Details Table")
        print("   ✓ Visual Charts (4 interactive charts)")
        print("   ✓ Professional Timestamp")
        print("   ✓ Dynamic Facility Name")
        
        print(f"\n🌐 Open in browser: file://{os.path.abspath(report_path)}")
        
    except Exception as e:
        print(f"❌ ERROR generating report: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
