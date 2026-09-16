# Facility Information Bulk Export

Automated bulk export of facility patient records. The tool logs into the facility portal, walks a patient list, downloads documents and tabular data, and stores everything in a consistent per-patient folder layout.

## What data is pulled

For each patient in the input CSV (`id`, `first_name`, `last_name`), the exporter collects:

| # | Data category | What is saved |
|---|---|---|
| 01 | Patient details | Profile fields (name, DOB, gender, contact, address, referral, pharmacy, notification settings, and related attributes) as a single-row CSV |
| 02 | Patient images | Clinical / patient images |
| 03 | Appointment history | Full appointment export converted to CSV (phone columns excluded) |
| 04 | Service history | Service list rows: Service Name, Package Name, Date Received, Appointment Date, Created on |
| 05 | Encounter history | Encounter PDFs |
| 06 | Consent form history | Consent form PDFs |
| 07 | Patient invoices | Invoice PDFs |
| 08 | Membership invoices | Membership invoice PDFs |
| 09 | Available credits | Booking, banked, e-gift, and referral credit balances in one CSV |
| 10 | SMS log history | Conversation log as CSV (`From`, `Message`, `Date`; emojis stripped) |

Also generated after each run:

- HTML execution report under `downloads/reports/`
- Detailed log under `downloads/logs/`

## Output folder arrangement

Root path:

```text
downloads/<Facility Name>/
└── {PatientId}_{FirstName}_{LastName}/
    ├── 01_Patient_Details/
    ├── 02_Patient_Images/
    ├── 03_Appointment_History/
    ├── 04_Service_History/
    ├── 05_Encounter_History/
    ├── 06_Consent_Form_History/
    ├── 07_Patient_Invoices/
    ├── 08_Membership_Invoices/
    ├── 09_Available_Credits/
    └── 10_SMS_Log_History/
```

Numeric prefixes keep this order when folders are sorted by name.

### Example patient folder

```text
downloads/Facility One(QA)/
└── 272300_Zensen_Shen/
    ├── 01_Patient_Details/
    │   └── Zensen Shen_details.csv
    ├── 02_Patient_Images/
    │   └── patient image …_Zensen Shen_MM-DD-YYYY.png
    ├── 03_Appointment_History/
    │   └── Appointment_History_Zensen Shen.csv
    ├── 04_Service_History/
    │   └── Service_History_Zensen Shen.csv
    ├── 05_Encounter_History/
    │   └── ProcedureName_Zensen Shen_MM-DD-YYYY.pdf
    ├── 06_Consent_Form_History/
    │   └── ConsentName_Zensen Shen_MM-DD-YYYY.pdf
    ├── 07_Patient_Invoices/
    │   └── Invoice_Zensen Shen_MM-DD-YYYY.pdf
    ├── 08_Membership_Invoices/
    │   └── MembershipInvoice_Zensen Shen_MM-DD-YYYY.pdf
    ├── 09_Available_Credits/
    │   └── All_Credits_Zensen Shen.csv
    └── 10_SMS_Log_History/
        └── SMS_Log_Zensen Shen.csv
```

## File naming conventions

| Type | Naming pattern |
|---|---|
| Patient details | `{PatientName}_details.csv` |
| Images | Original / cleaned name with patient and date |
| Appointments | `Appointment_History_{PatientName}.csv` |
| Services | `Service_History_{PatientName}.csv` |
| Encounters | `{ProcedureName}_{PatientName}_{MM-DD-YYYY}.pdf` (+ `_1`, `_2`, … if duplicates) |
| Consents | `{ConsentName}_{PatientName}_{MM-DD-YYYY}.pdf` (+ sequence if duplicates) |
| Invoices | `Invoice_{PatientName}_{MM-DD-YYYY}.pdf` (+ sequence if duplicates) |
| Membership invoices | `MembershipInvoice_{PatientName}_{MM-DD-YYYY}.pdf` |
| Credits | `All_Credits_{PatientName}.csv` |
| SMS log | `SMS_Log_{PatientName}.csv` |

Same-name / same-date PDFs are **not skipped** — sequence numbers are appended so every download is kept.

## Special CSV behaviors

- **Patient details:** one row; missing fields written as `N/A`
- **Service history:** blank cells → `N/A`; empty list → one row with `no data found for this patient`
- **Available credits:** always written (including `$0` rows); referral lines listed individually plus a total row
- **SMS log:** `From` is `Facility` or the patient name; empty conversation → `no data found for this patient`
- **Appointments:** empty appointment list → folder is left without an export file

## Requirements

- Python 3.8+
- Playwright
- PyYAML
- Valid portal credentials in `config/credentials.yaml` (not committed)
- App settings in `config/settings.yaml` (not committed)
- Patient list CSV with at least `id`, `first_name`, `last_name`

## Setup

```bash
pip install -r requirements.txt
playwright install
```

Create `config/credentials.yaml`:

```yaml
username: your_username
password: your_password
facility: Your Facility Name
```

Create `config/settings.yaml`:

```yaml
browser_mode: headed   # or headless
page_timeout: 60000
base_url: https://your-portal-host.example
viewport:
  width: 1725
  height: 973
```

Place the patient list CSV at the project root (see `.gitignore` — patient lists are not committed).

## Run

```bash
python src/main.py
```

Patients already fully exported (required document folders populated) are skipped unless newer records are detected.

## Notes

- Credentials, settings, patient lists, and `downloads/` stay local and are ignored by git.
- Reports and logs are written under `downloads/` for each run.
