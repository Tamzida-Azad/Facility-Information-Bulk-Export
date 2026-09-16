import asyncio
import os
import yaml
import csv
from auth import authenticate_and_select_facility
from encounter_downloader import download_encounter_documents
from consent_downloader import download_consent_documents
from invoice_downloader import download_invoice_documents
from image_downloader import download_patient_images
from membership_invoice_downloader import download_membership_invoices
from appointment_downloader import download_appointment_history
from credits_downloader import download_all_credits
from service_history_downloader import download_service_history
from sms_log_downloader import download_sms_log
from patient_details_downloader import download_patient_details
from logger import init_logger, get_logger
from report_generator import generate_execution_report

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config')
BASE_DOWNLOADS_PATH = os.path.join(os.path.dirname(__file__), '..', 'downloads', 'Facility One(QA)')
os.makedirs(BASE_DOWNLOADS_PATH, exist_ok=True)

# Patient subfolders in display/process serial order (numeric prefix keeps name-sort order)
PATIENT_SUBFOLDERS = [
    '01_Patient_Details',
    '02_Patient_Images',
    '03_Appointment_History',
    '04_Service_History',
    '05_Encounter_History',
    '06_Consent_Form_History',
    '07_Patient_Invoices',
    '08_Membership_Invoices',
    '09_Available_Credits',
    '10_SMS_Log_History',
]
FOLDER_DETAILS = PATIENT_SUBFOLDERS[0]
FOLDER_IMAGES = PATIENT_SUBFOLDERS[1]
FOLDER_APPOINTMENTS = PATIENT_SUBFOLDERS[2]
FOLDER_SERVICES = PATIENT_SUBFOLDERS[3]
FOLDER_ENCOUNTERS = PATIENT_SUBFOLDERS[4]
FOLDER_CONSENTS = PATIENT_SUBFOLDERS[5]
FOLDER_INVOICES = PATIENT_SUBFOLDERS[6]
FOLDER_MEMBERSHIP = PATIENT_SUBFOLDERS[7]
FOLDER_CREDITS = PATIENT_SUBFOLDERS[8]
FOLDER_SMS = PATIENT_SUBFOLDERS[9]

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_patient_ids(csv_path):
    """Load patient IDs from CSV file."""
    patient_ids = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            patient_id = row.get('id', '').strip()
            if patient_id:
                patient_ids.append(patient_id)
    return patient_ids

def to_pascalcase(text):
    """Convert text to Title Case (capitalize first letter of each word)."""
    return ' '.join(word.capitalize() for word in text.split())

def patient_already_processed(patient_folder_path):
    """Check if patient folder already has all required subfolders with content."""
    # Content-required folders used to decide if a patient was already fully exported.
    # CSV-only folders (appointments/credits/services/SMS) are created in serial order
    # during processing but are not all required to contain files for skip logic.
    required_folders = [
        FOLDER_IMAGES,
        FOLDER_ENCOUNTERS,
        FOLDER_CONSENTS,
        FOLDER_INVOICES,
        FOLDER_MEMBERSHIP,
    ]
    
    # Check if main patient folder exists
    if not os.path.exists(patient_folder_path):
        return False
    
    # Check if all required subfolders exist and have files
    for subfolder in required_folders:
        subfolder_path = os.path.join(patient_folder_path, subfolder)
        
        # Subfolder must exist
        if not os.path.exists(subfolder_path):
            return False
        
        # Subfolder must not be empty (has at least one file)
        if not os.listdir(subfolder_path):
            return False
    
    return True

def count_files_in_folder(folder_path):
    """Count the number of files in a folder."""
    if not os.path.exists(folder_path):
        return 0
    try:
        return len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
    except Exception:
        return 0

def rename_files_in_folder(folder_path, patient_name, document_type):
    """
    Rename files in a folder based on document type.
    
    Format conventions:
    - Encounter: 'ProcedureName_PatientName_MM-DD-YYYY_#.pdf'
      Example: 'Dermal Fillers_QA Tamzida_04-30-2026_1.pdf'
    - Consent: 'ConsentFormName_PatientName_MM-DD-YYYY_#.pdf'
      Example: 'Dermal Fillers_Mushfiq Rahman_01-20-2024_1.pdf'
    - Invoice: 'Invoice_PatientName_MM-DD-YYYY.pdf'
      Example: 'Invoice_Mushfiq Rahman_01-25-2024.pdf'
    - Image: 'FILENAME_PatientName_MM-DD-YYYY_#.{ext}'
      Example: 'patient_photo_Vip Patient_04-30-2026_1.jpg', 'scan_Vip Patient_04-30-2026_2.png'
    - Membership Invoice: 'MembershipInvoice_PatientName_MM-DD-YYYY.pdf'
      Example: 'MembershipInvoice_John Doe_04-30-2026.pdf'
    """
    if not os.path.exists(folder_path):
        return
    
    try:
        import re
        from datetime import datetime
        
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        for filename in files:
            # Extract file extension
            file_extension = os.path.splitext(filename)[1]
            
            # Try to extract document name and date from original filename
            name_without_ext = os.path.splitext(filename)[0]
            
            # Try to find a date pattern (YYYY-MM-DD or MM-DD-YYYY or other formats)
            date_match = re.search(r'\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{1,2}/\d{1,2}/\d{4}', name_without_ext)
            
            if date_match:
                # Date found - extract and convert to MM-DD-YYYY format
                date_str_raw = date_match.group()
                try:
                    # Try parsing YYYY-MM-DD format
                    if len(date_str_raw.split('-')[0]) == 4:
                        date_obj = datetime.strptime(date_str_raw, '%Y-%m-%d')
                    # Try parsing MM-DD-YYYY format
                    elif len(date_str_raw.split('-')[2]) == 4:
                        date_obj = datetime.strptime(date_str_raw, '%m-%d-%Y')
                    # Try parsing slash format MM/DD/YYYY
                    else:
                        date_obj = datetime.strptime(date_str_raw, '%m/%d/%Y')
                    date_str = date_obj.strftime('%m-%d-%Y')
                except Exception:
                    # If parsing fails, use current date
                    date_str = datetime.now().strftime('%m-%d-%Y')
                
                # Remove date from the name to get document name
                document_name = name_without_ext.replace(date_str_raw, '').strip('_- /')
                # Clean up the document name (replace underscores/slashes/time patterns with spaces)
                document_name = re.sub(r'_|\s+-\s+\d+:\d+\s*[ap]m', ' ', document_name, flags=re.IGNORECASE)
                document_name = document_name.replace('/', ' ').strip()
            else:
                # No date found - use current date
                date_str = datetime.now().strftime('%m-%d-%Y')
                # Use the filename without extension as document name
                document_name = re.sub(r'_|\s+-\s+\d+:\d+\s*[ap]m', ' ', name_without_ext, flags=re.IGNORECASE)
                document_name = document_name.replace('/', ' ').strip()
            
            # Format filename based on document type
            if document_type == 'Invoice':
                # Format: Invoice_PatientName_MM-DD-YYYY.extension
                new_filename = f"Invoice_{patient_name}_{date_str}{file_extension}"
            elif document_type == 'Consent':
                # Format: ConsentFormName_PatientName_MM-DD-YYYY_#.extension
                # Extract procedure name from parentheses if present
                consent_name = document_name
                
                # Look for procedure name in parentheses - improved regex
                procedure_match = re.search(r'\(([^)]+)\)', document_name)
                if procedure_match:
                    consent_name = procedure_match.group(1).strip()
                    print(f"  Extracted procedure from parentheses: '{consent_name}'")
                else:
                    # Clean up the document name - remove patient name prefix and time stamps
                    # Remove patient name from the beginning if present
                    patient_name_variants = [
                        patient_name,
                        patient_name.replace(' ', '_'),
                        patient_name.replace(' ', '').lower(),
                        patient_name.lower()
                    ]
                    
                    for variant in patient_name_variants:
                        if consent_name.lower().startswith(variant.lower()):
                            consent_name = consent_name[len(variant):].strip('_- ')
                            break
                    
                    # Remove common patterns like " - 6 01 am" or similar timestamps
                    consent_name = re.sub(r'\s*-\s*\d+\s+\d+\s+[ap]m.*$', '', consent_name, flags=re.IGNORECASE)
                    
                    # If nothing meaningful remains, use "Consent Form"
                    if not consent_name.strip():
                        consent_name = "Consent Form"
                    
                    print(f"  Cleaned consent name: '{consent_name}'")
                
                # Create base filename without sequence number
                base_filename = f"{consent_name}_{patient_name}_{date_str}"
                new_filename = f"{base_filename}{file_extension}"
                
                # Handle multiple consent forms with same date by adding sequence numbers
                final_path = os.path.join(folder_path, new_filename)
                if os.path.exists(final_path):
                    counter = 1
                    while True:
                        sequenced_filename = f"{base_filename}_{counter}{file_extension}"
                        final_path = os.path.join(folder_path, sequenced_filename)
                        if not os.path.exists(final_path):
                            new_filename = sequenced_filename
                            break
                        counter += 1
            elif document_type == 'Image':
                # Format: FILENAME_PatientName_MM-DD-YYYY_#.extension
                # Use the original filename (without extension) as the identifier
                # Clean up the document name and use it directly
                if document_name.strip():
                    # Remove common prefixes like "Image", "Photo", "IMG" etc.
                    clean_name = document_name
                    for prefix in ['Image_', 'Photo_', 'IMG_', 'image_', 'photo_', 'img_']:
                        if clean_name.startswith(prefix):
                            clean_name = clean_name[len(prefix):]
                    # If still has content, use it; otherwise use original
                    filename_base = clean_name if clean_name.strip() else document_name
                else:
                    # Use original filename without extension
                    filename_base = os.path.splitext(filename)[0]
                
                # Create base filename without sequence number
                base_filename = f"{filename_base}_{patient_name}_{date_str}"
                new_filename = f"{base_filename}{file_extension}"
                
                # Handle multiple files with same date by adding sequence numbers
                final_path = os.path.join(folder_path, new_filename)
                if os.path.exists(final_path):
                    counter = 1
                    while True:
                        sequenced_filename = f"{base_filename}_{counter}{file_extension}"
                        final_path = os.path.join(folder_path, sequenced_filename)
                        if not os.path.exists(final_path):
                            new_filename = sequenced_filename
                            break
                        counter += 1
            elif document_type == 'Membership Invoice':
                # Format: MembershipInvoice_PatientName_MM-DD-YYYY.extension
                new_filename = f"MembershipInvoice_{patient_name}_{date_str}{file_extension}"
            else:  # Encounter or other types
                # Format: ProcedureName_PatientName_MM-DD-YYYY_#.extension
                # Extract procedure name from parentheses if present
                encounter_name = document_name
                
                # Look for procedure name in parentheses - improved regex
                procedure_match = re.search(r'\(([^)]+)\)', document_name)
                if procedure_match:
                    encounter_name = procedure_match.group(1).strip()
                    print(f"  Extracted procedure from parentheses: '{encounter_name}'")
                else:
                    # Clean up the document name - remove patient name prefix and time stamps
                    # Remove patient name from the beginning if present
                    patient_name_variants = [
                        patient_name,
                        patient_name.replace(' ', '_'),
                        patient_name.replace(' ', '').lower(),
                        patient_name.lower()
                    ]
                    
                    for variant in patient_name_variants:
                        if encounter_name.lower().startswith(variant.lower()):
                            encounter_name = encounter_name[len(variant):].strip('_- ')
                            break
                    
                    # Remove common patterns like " - 6 01 am" or similar timestamps
                    encounter_name = re.sub(r'\s*-\s*\d+\s+\d+\s+[ap]m.*$', '', encounter_name, flags=re.IGNORECASE)
                    
                    # Remove other timestamp patterns
                    encounter_name = re.sub(r'\s*-\s*\d{1,2}:\d{2}\s*[ap]m.*$', '', encounter_name, flags=re.IGNORECASE)
                    
                    # If nothing meaningful remains, use "Encounter"
                    if not encounter_name.strip():
                        encounter_name = "Encounter"
                    
                    print(f"  Cleaned encounter name: '{encounter_name}'")
                
                # Create base filename without sequence number
                base_filename = f"{encounter_name}_{patient_name}_{date_str}"
                new_filename = f"{base_filename}{file_extension}"
                
                # Handle multiple encounters with same date by adding sequence numbers
                final_path = os.path.join(folder_path, new_filename)
                if os.path.exists(final_path):
                    counter = 1
                    while True:
                        sequenced_filename = f"{base_filename}_{counter}{file_extension}"
                        final_path = os.path.join(folder_path, sequenced_filename)
                        if not os.path.exists(final_path):
                            new_filename = sequenced_filename
                            break
                        counter += 1
            
            # Full paths
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            # Check if target filename already exists and add counter if needed
            if os.path.exists(new_path) and old_path != new_path:
                # Extract base name and extension
                base_name = os.path.splitext(new_filename)[0]
                ext = os.path.splitext(new_filename)[1]
                
                # Find next available number
                counter = 1
                while os.path.exists(os.path.join(folder_path, f"{base_name}_{counter}{ext}")):
                    counter += 1
                
                new_filename = f"{base_name}_{counter}{ext}"
                new_path = os.path.join(folder_path, new_filename)
            
            try:
                os.rename(old_path, new_path)
                print(f"  Renamed: {filename} → {new_filename}")
            except Exception as e:
                print(f"Warning: Could not rename {filename} to {new_filename}: {e}")
    except Exception as e:
        print(f"Warning: Error renaming files in {folder_path}: {e}")

async def check_if_new_records_pending(page, patient_id, patient_folder_path):
    """
    Check if there are new records pending to be downloaded.
    This function checks the system for updated record counts and compares with local downloads.
    """
    try:
        # Get current counts from the system for this patient
        encounter_count_system = await get_encounter_count_from_system(page, patient_id)
        invoice_count_system = await get_invoice_count_from_system(page, patient_id)
        consent_count_system = await get_consent_count_from_system(page, patient_id)
        
        # Get local downloaded counts
        encounter_path = os.path.join(patient_folder_path, FOLDER_ENCOUNTERS)
        invoice_path = os.path.join(patient_folder_path, FOLDER_INVOICES)
        
        encounter_count_local = count_files_in_folder(encounter_path)
        invoice_count_local = count_files_in_folder(invoice_path)
        
        consent_count_local = count_files_in_folder(os.path.join(patient_folder_path, FOLDER_CONSENTS))
        
        # Check if counts match
        if (encounter_count_local < encounter_count_system or 
            invoice_count_local < invoice_count_system or 
            consent_count_local < consent_count_system):
            return True  # New records pending
        
        return False  # All records are up to date
        
    except Exception as e:
        print(f"Warning: Could not check for new records: {e}. Re-downloading to be safe.")
        return True  # If we can't verify, re-download to be safe

async def get_encounter_count_from_system(page, patient_id):
    """Get the total count of encounters for a patient from the system."""
    # This should be implemented based on your system's UI/API
    # For now, returning a placeholder that you need to implement
    # You'll need to navigate to the encounters section and extract the count
    try:
        # Example: await page.goto(f'...encounters page for patient {patient_id}...')
        # count = await page.text_content('...count element selector...')
        # return int(count) or 0
        return 0
    except Exception:
        return 0

async def get_invoice_count_from_system(page, patient_id):
    """Get the total count of invoices for a patient from the system."""
    # This should be implemented based on your system's UI/API
    try:
        # Example: await page.goto(f'...invoices page for patient {patient_id}...')
        # count = await page.text_content('...count element selector...')
        # return int(count) or 0
        return 0
    except Exception:
        return 0

async def get_consent_count_from_system(page, patient_id):
    """Get the total count of consent forms for a patient from the system."""
    # This should be implemented based on your system's UI/API
    try:
        # Example: await page.goto(f'...consent page for patient {patient_id}...')
        # count = await page.text_content('...count element selector...')
        # return int(count) or 0
        return 0
    except Exception:
        return 0

def load_patient_data(csv_path):
    """Load patient data from CSV file."""
    patient_data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            patient_id = row.get('id', '').strip()
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            if patient_id and first_name and last_name:
                patient_data.append({
                    'id': patient_id,
                    'first_name': first_name,
                    'last_name': last_name
                })
    return patient_data

async def main():
    # Initialize logger
    log = init_logger(os.path.join(os.path.dirname(__file__), '..', 'downloads', 'logs'))
    
    # Path to CSV file with patient data
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'Facility QA Patients.csv')

    if not os.path.exists(csv_path):
        log.error(f"CSV file not found at {csv_path}")
        log.info("Please create a CSV file with 'id', 'first_name', and 'last_name' columns.")
        return

    # Load patient data from CSV
    patient_data = load_patient_data(csv_path)
    if not patient_data:
        log.error("No valid patient data found in CSV file.")
        return

    log.section("STARTING EMR DOCUMENT DOWNLOAD")
    log.info(f"Found {len(patient_data)} patient(s) to process.")

    # Load credentials and settings
    credentials = load_yaml(os.path.join(CONFIG_PATH, 'credentials.yaml'))
    settings = load_yaml(os.path.join(CONFIG_PATH, 'settings.yaml'))

    # Authenticate and select facility (once for all patients)
    log.info("Authenticating with EMR system...")
    playwright, browser, context, page = await authenticate_and_select_facility(credentials, settings)
    log.success("Authentication successful!")

    # Download encounter documents for each patient
    processed_count = 0
    skipped_count = 0
    total_files_downloaded = 0
    patients_report_data = []
    
    for idx, patient in enumerate(patient_data, 1):
        patient_id = patient['id']
        first_name = patient['first_name']
        last_name = patient['last_name']
        
        # Convert names to Title Case
        first_name_pascal = to_pascalcase(first_name)
        last_name_pascal = to_pascalcase(last_name)
        full_name = f"{first_name_pascal} {last_name_pascal}"
        
        folder_name = f"{patient_id}_{first_name_pascal}_{last_name_pascal}"
        patient_folder_path = os.path.join(BASE_DOWNLOADS_PATH, folder_name)
        
        # Log patient start
        log.patient_start(patient_id, first_name, last_name, idx, len(patient_data))
        
        # Check if patient already processed
        if patient_already_processed(patient_folder_path):
            # Double-check if new records have been added to the system
            has_new_records = await check_if_new_records_pending(page, patient_id, patient_folder_path)
            if not has_new_records:
                log.patient_skipped(patient_id, first_name, last_name)
                skipped_count += 1
                continue
            else:
                log.warning(f"Patient has new records - re-downloading")
        
        try:
            # Create patient subfolders in the required serial order
            for subfolder in PATIENT_SUBFOLDERS:
                os.makedirs(os.path.join(patient_folder_path, subfolder), exist_ok=True)

            # 1) Patient details CSV
            log.patient_download_start('Patient Details', full_name)
            details_download_path = os.path.join(patient_folder_path, FOLDER_DETAILS)
            details_count = await download_patient_details(
                page,
                details_download_path,
                patient_id=patient_id,
                patient_name=full_name
            )
            log.patient_download_complete('Patient Details', details_count, full_name)
            total_files_downloaded += details_count
            
            # 2) Patient images
            log.patient_download_start('Image', full_name)
            images_download_path = os.path.join(patient_folder_path, FOLDER_IMAGES)
            await download_patient_images(page, images_download_path, patient_id=patient_id, per_page=10, patient_name=full_name)
            rename_files_in_folder(images_download_path, full_name, 'Image')
            images_count = count_files_in_folder(images_download_path)
            log.patient_download_complete('Image', images_count, full_name)
            total_files_downloaded += images_count
            
            # 3) Appointment history (skipped when list is empty)
            log.patient_download_start('Appointment History', full_name)
            appointment_download_path = os.path.join(patient_folder_path, FOLDER_APPOINTMENTS)
            appointment_count = await download_appointment_history(
                page,
                appointment_download_path,
                patient_id=patient_id,
                patient_name=full_name
            )
            log.patient_download_complete('Appointment History', appointment_count, full_name)
            total_files_downloaded += appointment_count
            
            # 4) Service history
            log.patient_download_start('Service History', full_name)
            service_download_path = os.path.join(patient_folder_path, FOLDER_SERVICES)
            service_count = await download_service_history(
                page,
                service_download_path,
                patient_id=patient_id,
                patient_name=full_name
            )
            log.patient_download_complete('Service History', service_count, full_name)
            total_files_downloaded += service_count
            
            # 5) Encounters
            log.patient_download_start('Encounter', full_name)
            patient_download_path = os.path.join(patient_folder_path, FOLDER_ENCOUNTERS)
            await download_encounter_documents(page, patient_download_path, patient_id=patient_id, per_page=10)
            rename_files_in_folder(patient_download_path, full_name, 'Encounter')
            encounter_count = count_files_in_folder(patient_download_path)
            log.patient_download_complete('Encounter', encounter_count, full_name)
            total_files_downloaded += encounter_count
            
            # 6) Consent forms
            log.patient_download_start('Consent', full_name)
            consent_download_path = os.path.join(patient_folder_path, FOLDER_CONSENTS)
            await download_consent_documents(page, consent_download_path, patient_id=patient_id, per_page=10)
            rename_files_in_folder(consent_download_path, full_name, 'Consent')
            consent_count = count_files_in_folder(consent_download_path)
            log.patient_download_complete('Consent', consent_count, full_name)
            total_files_downloaded += consent_count
            
            # 7) Patient invoices
            log.patient_download_start('Invoice', full_name)
            invoice_download_path = os.path.join(patient_folder_path, FOLDER_INVOICES)
            await download_invoice_documents(page, invoice_download_path, patient_id=patient_id, per_page=10)
            rename_files_in_folder(invoice_download_path, full_name, 'Invoice')
            invoice_count = count_files_in_folder(invoice_download_path)
            log.patient_download_complete('Invoice', invoice_count, full_name)
            total_files_downloaded += invoice_count
            
            # 8) Membership invoices
            log.patient_download_start('Membership Invoice', full_name)
            membership_download_path = os.path.join(patient_folder_path, FOLDER_MEMBERSHIP)
            await download_membership_invoices(page, membership_download_path, patient_id=patient_id, per_page=10)
            rename_files_in_folder(membership_download_path, full_name, 'Membership Invoice')
            membership_count = count_files_in_folder(membership_download_path)
            log.patient_download_complete('Membership Invoice', membership_count, full_name)
            total_files_downloaded += membership_count
            
            # 9) Available credits
            log.patient_download_start('Available Credits', full_name)
            credits_download_path = os.path.join(patient_folder_path, FOLDER_CREDITS)
            credits_count = await download_all_credits(
                page,
                credits_download_path,
                patient_id=patient_id,
                patient_name=full_name
            )
            log.patient_download_complete('Available Credits', credits_count, full_name)
            total_files_downloaded += credits_count
            
            # 10) SMS log
            log.patient_download_start('SMS Log', full_name)
            sms_download_path = os.path.join(patient_folder_path, FOLDER_SMS)
            sms_count = await download_sms_log(
                page,
                sms_download_path,
                patient_id=patient_id,
                patient_name=full_name
            )
            log.patient_download_complete('SMS Log', sms_count, full_name)
            total_files_downloaded += sms_count
            
            log.patient_complete(patient_id, first_name, last_name)
            processed_count += 1
            
            # Track patient data for report
            patients_report_data.append({
                'patient_id': patient_id,
                'patient_name': full_name,
                'status': 'Completed',
                'patient_details': details_count,
                'encounters': encounter_count,
                'consent_forms': consent_count,
                'invoices': invoice_count,
                'images': images_count,
                'membership_invoices': membership_count,
                'appointment_history': appointment_count,
                'available_credits': credits_count,
                'service_history': service_count,
                'sms_log': sms_count,
                'total_files': details_count + encounter_count + consent_count + invoice_count + images_count + membership_count + appointment_count + credits_count + service_count + sms_count
            })
            
        except Exception as e:
            log.error(f"Failed to process patient {patient_id} ({first_name} {last_name}): {str(e)}")
            processed_count += 1
            
            # Track failed patient for report
            patients_report_data.append({
                'patient_id': patient_id,
                'patient_name': full_name,
                'status': 'Failed',
                'patient_details': 0,
                'encounters': 0,
                'consent_forms': 0,
                'invoices': 0,
                'images': 0,
                'membership_invoices': 0,
                'appointment_history': 0,
                'available_credits': 0,
                'service_history': 0,
                'sms_log': 0,
                'total_files': 0
            })

    await browser.close()
    await playwright.stop()
    
    log.summary(len(patient_data), processed_count, skipped_count, total_files_downloaded)
    
    # Generate HTML execution report
    log.info("Generating execution report...")
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'downloads', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Get facility name from credentials
    facility_name = credentials.get('facility', 'Facility One (QA)')
    facility_name_safe = facility_name.replace(' ', '_').replace('(', '').replace(')', '')
    
    # Generate report with facility name and date
    from datetime import datetime
    report_date = datetime.now().strftime('%m-%d-%Y')
    report_filename = f"{facility_name_safe}_Export_Report_{report_date}.html"
    
    report_data = {
        'facility_name': facility_name,  # Pass actual facility name for display
        'total_patients': len(patient_data),
        'processed_patients': processed_count,
        'skipped_patients': skipped_count,
        'total_files_downloaded': total_files_downloaded,
        'patients': patients_report_data
    }
    
    report_path = generate_execution_report(report_data, reports_dir, report_filename)
    log.success(f"Report generated: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())