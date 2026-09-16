#!/usr/bin/env python3
"""
Standalone Report Generator Test
Generates a sample HTML report to test the report functionality independently.
"""

import os
import sys
sys.path.append('src')

from report_generator import generate_execution_report

def main():
    """Generate a test report with sample data."""
    
    print("🔄 Generating test EMR export report...")
    
    # Sample test data - mimics real execution results
    test_data = {
        'facility_name': 'Facility One (QA)',
        'total_patients': 8,
        'processed_patients': 7,
        'skipped_patients': 1,
        'total_files_downloaded': 47,
        'patients': [
            {
                'patient_id': '156640',
                'patient_name': 'Vip Patient',
                'status': 'Completed',
                'encounters': 3,
                'consent_forms': 2,
                'invoices': 2,
                'images': 7,
                'membership_invoices': 1,
                'total_files': 15
            },
            {
                'patient_id': '193680',
                'patient_name': 'Ashik Patient',
                'status': 'Completed',
                'encounters': 2,
                'consent_forms': 1,
                'invoices': 3,
                'images': 4,
                'membership_invoices': 0,
                'total_files': 10
            },
            {
                'patient_id': '233957',
                'patient_name': 'Qa Tamzida',
                'status': 'Completed',
                'encounters': 1,
                'consent_forms': 2,
                'invoices': 1,
                'images': 5,
                'membership_invoices': 1,
                'total_files': 10
            },
            {
                'patient_id': '237213',
                'patient_name': 'Patient Mahmudur',
                'status': 'Completed',
                'encounters': 2,
                'consent_forms': 1,
                'invoices': 2,
                'images': 2,
                'membership_invoices': 0,
                'total_files': 7
            },
            {
                'patient_id': '251785',
                'patient_name': 'Mahmudur One',
                'status': 'Completed',
                'encounters': 1,
                'consent_forms': 0,
                'invoices': 1,
                'images': 1,
                'membership_invoices': 0,
                'total_files': 3
            },
            {
                'patient_id': '255347',
                'patient_name': 'Rajib Chowdhury',
                'status': 'Failed',
                'encounters': 0,
                'consent_forms': 0,
                'invoices': 0,
                'images': 0,
                'membership_invoices': 0,
                'total_files': 0
            },
            {
                'patient_id': '257296',
                'patient_name': 'Mohit Patient',
                'status': 'Completed',
                'encounters': 1,
                'consent_forms': 1,
                'invoices': 0,
                'images': 1,
                'membership_invoices': 0,
                'total_files': 3
            },
            {
                'patient_id': '264834',
                'patient_name': 'Arafat Hossain',
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
