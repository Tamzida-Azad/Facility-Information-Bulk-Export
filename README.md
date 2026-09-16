# CalystaPro EMR Patient Data Management

## Overview

**CalystaPro EMR Patient Data Management** is an automated Python-based solution designed to streamline the extraction, organization, and delivery of patient healthcare records from the CalystaPro EMR (Electronic Medical Records) system. This tool efficiently manages the download and standardization of critical patient documents while maintaining data integrity and preventing duplicate processing.

## Purpose

This script automates the tedious manual process of:
- ✅ Downloading patient encounter histories
- ✅ Retrieving consent forms
- ✅ Extracting invoice documents
- ✅ Capturing patient images
- ✅ Retrieving membership invoices
- ✅ Organizing files into standardized folder structures
- ✅ Renaming files with consistent, self-identifying formats
- ✅ Preventing reprocessing of already-downloaded patient records
- ✅ Detecting new records and updating existing patient data
- ✅ Generating comprehensive HTML execution reports

### Use Case
Perfect for healthcare facilities that need to:
- Bulk export patient records from CalystaPro EMR
- Prepare patient data for delivery to other systems or stakeholders
- Maintain organized, standardized file naming conventions
- Automate recurring data extraction workflows
- Ensure data consistency across multiple batch runs
- Track execution metrics and patient processing statistics

## Key Features

### 🔄 Smart Patient Processing
- **Automatic Skip Logic**: Prevents reprocessing of already-completed patients
- **Record Verification**: Compares local files with system records to detect new data
- **Batch Processing**: Handles multiple patients in a single execution
- **Resumable Execution**: Continue from where you left off on interrupted runs
- **Duplicate Detection**: Handles multiple files with same date/name with sequential counters

### 📁 Organized File Structure
```
downloads/Facility One(QA)/
├── 265145_Mushfiq_Rahman/
│   ├── Encounter_History/
│   │   ├── Dermal Fillers_Mushfiq Rahman_04-30-2026.pdf
│   │   └── Consultation_Mushfiq Rahman_04-28-2026.pdf
│   ├── Consent_Form_History/
│   │   └── Consent Form_Mushfiq Rahman_01-20-2024.pdf
│   ├── Patient_Invoices/
│   │   └── Invoice_Mushfiq Rahman_01-25-2024.pdf
│   ├── Patient_Images/
│   │   ├── Image_XRay_Mushfiq Rahman_04-30-2026.jpg
│   │   └── Image_Photo_Mushfiq Rahman_04-25-2026.png
│   └── Membership_Invoices/
│       └── MembershipInvoice_Mushfiq Rahman_04-30-2026.pdf
└── 264833_Lamia_Dama/
    └── [Similar structure...]
```

### 📝 Intelligent File Naming
Files are automatically renamed to include critical metadata:

| Document Type | Format | Example |
|---|---|---|
| **Encounter** | `ProcedureName_PatientName_MM-DD-YYYY.pdf` | `Dermal Fillers_Mushfiq Rahman_04-30-2026.pdf` |
| **Consent** | `ConsentFormName_PatientName_MM-DD-YYYY.pdf` | `Consent Form_Mushfiq Rahman_01-20-2024.pdf` |
| **Invoice** | `Invoice_PatientName_MM-DD-YYYY.pdf` | `Invoice_Mushfiq Rahman_01-25-2024.pdf` |
| **Image** | `Image_Identifier_PatientName_MM-DD-YYYY.ext` | `Image_XRay_Mushfiq Rahman_04-30-2026.jpg` |
| **Membership Invoice** | `MembershipInvoice_PatientName_MM-DD-YYYY.pdf` | `MembershipInvoice_Mushfiq Rahman_04-30-2026.pdf` |

**Benefit**: Files are self-identifying - even if moved outside their folders, you can still identify the patient and document type.

### 📊 Professional HTML Reports
Automatic generation of comprehensive execution reports:
- **Summary Statistics**: Total patients, completed, skipped, files downloaded
- **Patient Details Table**: Individual patient processing status
- **Interactive Charts**: 
  - Patient status distribution (pie chart)
  - Documents by type (bar chart)
  - File success rates (doughnut chart)
  - Distribution by document type
- **Real-time Metrics**: Efficiency percentages and success rates
- **Report Location**: `downloads/reports/Facility_Name_Export_Report_MM-DD-YYYY.html`

### 📋 Comprehensive Logging
- **Terminal Output**: Clean, readable logs with emojis and progress indicators
- **File Logging**: Complete audit trail in `downloads/logs/execution_YYYYMMDD_HHMMSS.log`
- **Progress Tracking**: Patient counter format `[current/total]`
- **Dual Output**: Console + file-based audit trail for compliance

### 🔐 Browser Automation
- Uses **Playwright** for reliable web automation
- Supports headless and headed modes
- Configurable timeouts and viewport settings
- Automatic login and facility selection
- Robust error handling and recovery

## Requirements

- Python 3.8+
- Playwright
- PyYAML
- Valid CalystaPro EMR credentials
- Access to the EMR system

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/CalystaPro-EMR-Manager.git
cd CalystaPro-EMR-Manager

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## Configuration

### 1. **credentials.yaml** - EMR Credentials
```yaml
username: your_emr_username
password: your_emr_password
facility: Facility One(QA)
```

### 2. **settings.yaml** - Application Settings
```yaml
browser_mode: headed  # 'headed' for testing, 'headless' for production
page_timeout: 60000   # in milliseconds
base_url: https://www.calystaproemr.com
viewport:
  width: 1725
  height: 973
```

### 3. **Facility 1 QA Patients.csv** - Patient List
```csv
id,first_name,last_name
265145,Mushfiq,Rahman
264833,Lamia,Dama
237213,Mahmudur,Rahman
```

## Usage

### Basic Execution
```bash
python src/main.py
```

### Expected Output
```
============================================================
                 🏥 EMR DOCUMENT DOWNLOADER 🏥
============================================================

Found 19 patient(s) to process.
Authenticating with EMR system...
✓ Authentication successful!

[1/19] Processing patient: 265145 (Mushfiq Rahman)
  🏥 Downloading Encounters...
    Renamed: encounter_001.pdf → Dermal Fillers_Mushfiq Rahman_04-30-2026.pdf
    Renamed: encounter_002.pdf → Consultation_Mushfiq Rahman_04-30-2026_1.pdf
  ✓ Encounter downloads complete: 2 files
  
  📝 Downloading Consent Forms...
    Renamed: consent_form.pdf → Consent Form_Mushfiq Rahman_01-20-2024.pdf
  ✓ Consent downloads complete: 1 file
  
  💳 Downloading Invoices...
    Renamed: invoice_001.pdf → Invoice_Mushfiq Rahman_01-25-2024.pdf
  ✓ Invoice downloads complete: 1 file
  
  🖼 Downloading Patient Images...
    Renamed: xray_scan.jpg → Image_XRay_Mushfiq Rahman_04-30-2026.jpg
  ✓ Image downloads complete: 1 file
  
  💼 Downloading Membership Invoices...
    Renamed: membership_invoice.pdf → MembershipInvoice_Mushfiq Rahman_04-30-2026.pdf
  ✓ Membership Invoice downloads complete: 1 file
  
✓ Patient 265145 processing complete

[2/19] Processing patient: 264833 (Lamia Dama)
✓ Patient already processed - Skipping (verified up-to-date)

============================================================
Summary: Processed 18 patient(s), Skipped 1 patient(s)
Total Files Downloaded: 127
Generating execution report...
✓ Report generated: downloads/reports/Facility_One_Export_Report_04-30-2026.html
============================================================
```

## Testing Scenarios

### Test Case 1: New Patient (No Previous Downloads)
- **Expected**: All five document types downloaded and renamed
- **Verify**: Folder structure created, files exist, naming follows convention

### Test Case 2: Already Processed Patient (No New Records)
- **Expected**: Patient skipped, no downloads
- **Verify**: Skip message printed, file counts unchanged

### Test Case 3: Previously Processed Patient (New Records Added)
- **Expected**: New documents downloaded and integrated
- **Verify**: Updated file counts reflect new records

### Test Case 4: Multiple Documents with Same Date
- **Expected**: Sequential counters added to prevent overwrites
- **Verify**: Files named with `_1`, `_2` suffixes

### Test Case 5: Empty Document Type
- **Expected**: Empty folder created, no errors
- **Verify**: `patient_already_processed()` returns False for incomplete patients

### Test Case 6: Invalid CSV Data
- **Expected**: Rows with missing fields skipped
- **Verify**: Only valid patients processed

### Test Case 7: File Renaming Edge Cases
- Various date formats in original filenames
- Filenames without dates (uses current date)
- Special characters in document names

## Project Structure

```
CalystaPro-EMR-Manager/
├── src/
│   ├── main.py                          # Main execution script & orchestration
│   ├── auth.py                          # EMR authentication
│   ├── encounter_downloader.py          # Encounter document retrieval
│   ├── consent_downloader.py            # Consent form retrieval
│   ├── invoice_downloader.py            # Invoice document retrieval
│   ├── image_downloader.py              # Patient image retrieval
│   ├── membership_invoice_downloader.py # Membership invoice retrieval
│   ├── encounter_selectors.py           # UI element selectors
│   ├── consent_selectors.py             # UI element selectors
│   ├── invoice_selectors.py             # UI element selectors
│   ├── image_selectors.py               # UI element selectors
│   ├── login_selectors.py               # Login UI selectors
│   ├── logger.py                        # Clean logging system
│   ├── checkpoint_manager.py            # Progress tracking
│   ├── file_manager.py                  # File operations
│   ├── validator.py                     # Data validation
│   └── report_generator.py              # HTML report generation
├── config/
│   ├── credentials.yaml                 # EMR login credentials
│   ├── settings.yaml                    # Application configuration
├── downloads/
│   ├── Facility One(QA)/                # Downloaded files organized here
│   ├── reports/                         # HTML execution reports
│   └── logs/                            # Execution audit logs
├── Facility 1 QA Patients.csv           # Input patient data
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## Key Functions

### `patient_already_processed(patient_folder_path)`
Validates if a patient's folder contains all required documents with content:
- Checks for Encounter_History folder with files
- Checks for Patient_Invoices folder with files
- Checks for Consent_Form_History folder with files
- Checks for Patient_Images folder with files
- Checks for Membership_Invoices folder with files
- Returns `True` only if all conditions met

### `check_if_new_records_pending(page, patient_id, patient_folder_path)`
Compares local downloads with system records:
- Queries system for current record counts
- Counts local downloaded files
- Returns `True` if new records detected
- Safe fallback: re-downloads if verification fails

### `rename_files_in_folder(folder_path, patient_name, document_type)`
Standardizes file naming with patient identification:
- Extracts date from original filename
- Converts date to MM-DD-YYYY format
- Applies document-type-specific naming conventions
- Handles files without dates (uses current date)
- Handles duplicate names with sequential counters

### `to_pascalcase(text)`
Converts text to Title Case:
- Capitalizes first letter of each word
- Ensures consistent patient name formatting

## Error Handling

The script includes robust error handling for:
- ✅ Network timeouts (configurable timeout in settings)
- ✅ Missing configuration files
- ✅ Invalid CSV data
- ✅ File renaming failures
- ✅ EMR connection issues
- ✅ Dialog handling errors
- ✅ File duplication conflicts

## Performance

- **Typical Processing Time**: ~2-3 minutes per patient (depends on EMR response time)
- **Batch Size**: 19 patients tested successfully
- **Skip Optimization**: Already-processed patients skipped in <1 second
- **File Operations**: Efficient batch renaming and organizing

## File Organization Benefits

1. **Self-Identifying Files**: Patient name and date in filename
2. **Consistent Format**: All files follow same naming convention
3. **Easy Searching**: Find files by patient name or date
4. **Compliance Ready**: Audit trails with complete logging
5. **Duplicate Prevention**: Sequential numbering prevents overwrites
6. **Organized Folders**: Document types in separate folders
7. **Portable Data**: Files can be moved while remaining identifiable

## Report Generation

### Automatic Report Creation
After each execution, an HTML report is automatically generated with:
- **File Location**: `downloads/reports/{FacilityName}_Export_Report_{MM-DD-YYYY}.html`
- **Open in Browser**: Double-click to view results
- **Interactive Charts**: Hover for detailed statistics
- **Complete Audit Trail**: All patient processing details

### Report Includes
- Total patients processed
- Success/failure statistics
- File count by document type
- Individual patient details
- Processing efficiency metrics
- Visual analytics and charts

## Future Enhancements

- [ ] Database integration for persistent state tracking
- [ ] Email notifications on completion
- [ ] Parallel patient processing
- [ ] Enhanced logging and audit trails
- [ ] Support for additional document types
- [ ] API endpoint for on-demand processing
- [ ] Web dashboard for monitoring
- [ ] Automated scheduling with cron jobs

## Troubleshooting

### Timeout Errors
- Increase `page_timeout` in `settings.yaml` (in milliseconds)
- Check internet connectivity
- Verify EMR system is accessible
- **Solution**: Change `page_timeout: 60000` to `page_timeout: 90000`

### Authentication Failures
- Verify credentials in `credentials.yaml`
- Ensure facility name matches exactly
- Check if account has active session
- **Solution**: Test credentials manually in browser first

### File Renaming Issues
- Verify source files have readable dates
- Check folder permissions
- Review logs for specific error messages
- **Solution**: Check `downloads/logs/` for detailed error messages

### Duplicate File Handling
- Multiple files with same date get sequential counters
- Verify no naming conflicts in folder
- **Solution**: Manual review and consolidation if needed

### Missing HTML Report
- Check `downloads/reports/` directory exists
- Verify write permissions on directory
- Check console for generation errors
- **Solution**: Create `downloads/reports/` folder manually

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Changelog

### Version 1.0 (Current)
- ✅ 5 document types support (Encounters, Consent, Invoices, Images, Membership Invoices)
- ✅ Smart skip logic with duplicate detection
- ✅ Professional HTML report generation
- ✅ Clean logging with dual output (console + file)
- ✅ Intelligent file renaming with date extraction
- ✅ Sequential counter handling for duplicates
- ✅ Comprehensive error handling
- ✅ Browser automation with Playwright

## Author

CalystaPro EMR Patient Data Management Tool
- **Purpose**: Streamline healthcare data extraction and organization
- **Built For**: Healthcare facilities using CalystaPro EMR
- **Last Updated**: April 2026
- **Version**: 1.0

---

**⚠️ Important**: This tool handles sensitive healthcare data. Ensure compliance with HIPAA and local privacy regulations. Always use in secure environments and restrict access to authorized personnel only.

**📊 Dashboard Available**: Open the generated HTML reports to view interactive charts and statistics from your executions.

**✅ All Systems Go**: Your automation workflow is ready to process patient records efficiently!
