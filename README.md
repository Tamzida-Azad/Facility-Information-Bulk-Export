# Facility Information Bulk Export

Browser-based automation that bulk-exports **patient records from a facility EMR portal** into a clean, per-patient folder package. It logs in, selects the facility, walks your patient list, and downloads the same documents and histories a staff member would open one patient at a time—without requiring direct database access.

## Why this exists (when a database export is not enough)

Many migrations, audits, and handoffs need **the records as the clinic actually sees them**—not only rows in tables.

A SQL / DB dump often falls short because:

| What you need | Why the DB alone is awkward |
|---|---|
| **Invoice PDFs** | Final invoices are usually rendered documents (layout, line items, payments). Tables may hold fragments; the PDF is the legal / operational artifact. |
| **Encounter / chart PDFs** | Clinical notes and procedure docs are generated views or stored files—not a single readable “chart” column. |
| **Consent form PDFs** | Signed consents live as documents (or document pipelines), not plain text rows. |
| **Patient images** | Photos and clinical images are binary assets behind the UI or object storage—not CSV-friendly. |
| **Incoming / outgoing SMS** | Conversation history is threaded UI content; DB fields may be incomplete, encoded, or split across services. |

This automation is helpful when you need a **faithful, patient-by-patient file package** for:

- Facility migration or EMR cutover  
- Client delivery of historical records  
- Compliance / audit archives where PDFs and images matter  
- Cases where you have **portal access** but not a practical bulk-document API or DB map  

It does **not** replace a warehouse for analytics. It complements (or substitutes for) DB export when the deliverable is **documents + readable histories**.

## What this automation delivers

For every patient in the input list, it builds:

```text
downloads/<Facility Name>/{PatientId}_{FirstName}_{LastName}/
├── 01_Patient_Details/          → profile CSV
├── 02_Patient_Images/           → clinical / patient images
├── 03_Appointment_History/      → appointments CSV
├── 04_Service_History/          → services CSV
├── 05_Encounter_History/        → encounter PDFs
├── 06_Consent_Form_History/     → consent PDFs
├── 07_Patient_Invoices/         → invoice PDFs
├── 08_Membership_Invoices/      → membership invoice PDFs
├── 09_Available_Credits/        → credits CSV
└── 10_SMS_Log_History/          → SMS conversation CSV
```

Also produced after runs:

- **Execution / progress HTML reports** under `downloads/reports/`
- **Client delivery HTML** via `python src/generate_client_delivery_report.py`
- **Run logs** under `downloads/logs/` (and optional supervised overnight log)

Built for long facilities: **resume** (skip finished categories), **Phase 1 incomplete → Phase 2 new patients**, multi-worker browsers, and an optional **supervisor** that auto-restarts and backs off workers on memory/browser crashes.

## What input it needs

| Input | Required | Description |
|---|---|---|
| Patient list CSV | **Yes** | Columns: `id`, `first_name`, `last_name` (extra columns OK). Place in the **project root** (same folder as this README). |
| `config/credentials.yaml` | **Yes** | Portal username, password, and **exact** facility label from the portal dropdown. Copy from `config/credentials.example.yaml`. **Not committed.** |
| `config/settings.yaml` | **Yes** | Portal URL, browser mode, timeouts, workers, optional supervisor. Copy from `config/settings.example.yaml`. **Not committed.** |

CSV selection on startup:

1. Scans the project root for valid patient CSVs  
2. If several exist, prefers a filename matching `facility` from credentials; otherwise newest file  
3. Writes under `downloads/<Facility Name>/`

## Backend / tools required to set it up

This is a **local automation client**, not a hosted backend service. You need:

| Requirement | Purpose |
|---|---|
| **Python 3.8+** | Runtime |
| **pip** + `requirements.txt` | Installs `playwright`, `pyyaml`, `aiofiles` |
| **Playwright browsers** (`playwright install`) | Chromium to drive the EMR UI — **required**; pip alone is not enough |
| **Network access** to the EMR portal | Login + downloads |
| **Valid portal user** with rights to open patients, docs, invoices, SMS, images | Same permissions a staff export would need |
| **Disk space** | PDF/image-heavy facilities can be tens of GB |
| **OS** | Windows / macOS / Linux where Playwright is supported |

### Setup (do this in order)

```bash
git clone https://github.com/Tamzida-Azad/Facility-Information-Bulk-Export.git
cd Facility-Information-Bulk-Export

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

Create config from the examples (filenames must be exact):

```bash
cp config/credentials.example.yaml config/credentials.yaml
cp config/settings.example.yaml config/settings.yaml
```

Edit `config/credentials.yaml` and `config/settings.yaml`, then place a patient CSV in the project root.

### Common setup failures (and fixes)

| Symptom | Likely cause | Fix |
|---|---|---|
| `FileNotFoundError` for `credentials.yaml` / `settings.yaml` | Examples not copied | Copy `*.example.yaml` → `credentials.yaml` / `settings.yaml` |
| Browser / Playwright errors on first run | Browsers not installed | Run `playwright install chromium` |
| `Facility '…' not found in global-facility select` | Facility string ≠ portal dropdown | Copy the label exactly (spaces, dashes, casing) |
| `No patient list CSV found` | CSV missing or wrong columns | Put CSV in project root with `id`, `first_name`, `last_name` |
| Workers crash / MemoryError overnight | Too many browsers for RAM | Lower `worker_count` (e.g. 5→3→2) or use `watch_export.py` |
| Login failed | Bad credentials or portal URL | Check username/password and `base_url` in settings |

## What data is pulled (detail)

| # | Category | Saved as |
|---|---|---|
| 01 | Patient details | Single-row CSV (profile, contact, address, referral, pharmacy, notifications, …) |
| 02 | Patient images | Image files |
| 03 | Appointment history | CSV (phone columns excluded) |
| 04 | Service history | CSV (service / package / dates) |
| 05 | Encounter history | PDFs |
| 06 | Consent form history | PDFs |
| 07 | Patient invoices | PDFs |
| 08 | Membership invoices | PDFs |
| 09 | Available credits | One CSV (booking, banked, e-gift, referral) |
| 10 | SMS log history | CSV (`From`, `Message`, `Date`; emojis stripped) |

### Example patient folder

```text
downloads/Example Clinic (Demo)/
└── 100001_Jane_Example/
    ├── 01_Patient_Details/
    │   └── Jane Example_details.csv
    ├── 02_Patient_Images/
    │   └── patient image …_Jane Example_MM-DD-YYYY.png
    ├── 03_Appointment_History/
    │   └── Appointment_History_Jane Example.csv
    ├── 04_Service_History/
    │   └── Service_History_Jane Example.csv
    ├── 05_Encounter_History/
    │   └── ProcedureName_Jane Example_MM-DD-YYYY.pdf
    ├── 06_Consent_Form_History/
    │   └── ConsentName_Jane Example_MM-DD-YYYY.pdf
    ├── 07_Patient_Invoices/
    │   └── Invoice_Jane Example_MM-DD-YYYY.pdf
    ├── 08_Membership_Invoices/
    │   └── MembershipInvoice_Jane Example_MM-DD-YYYY.pdf
    ├── 09_Available_Credits/
    │   └── All_Credits_Jane Example.csv
    └── 10_SMS_Log_History/
        └── SMS_Log_Jane Example.csv
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

Same-name / same-date PDFs are **not skipped**—sequence numbers are appended so every download is kept.

## Special CSV behaviors

- **Patient details:** one row; missing fields written as `N/A`
- **Service history:** blank cells → `N/A`; empty list → one row with `no data found for this patient`
- **Available credits:** always written (including `$0` rows); referral lines listed individually plus a total row
- **SMS log:** `From` is `Facility` or the patient name; empty conversation → `no data found for this patient`
- **Appointments:** empty appointment list → folder may be left without an export file

## Run

```bash
python src/main.py
```

- Finished patients (all categories done) are skipped unless newer portal records are detected  
- Incomplete patients are finished first (**Phase 1**), then not-yet-started patients (**Phase 2**)

### Unattended overnight runs

```bash
python src/watch_export.py
# or:
python src/watch_export.py --log export.log
```

On MemoryError / dead browser / idle hang, the supervisor restarts, resumes incomplete-first, and can step workers down (e.g. 5 → 3 → 2). Configure under `supervisor:` in `config/settings.yaml`. State: `downloads/export_supervisor_state.json`.

### Client-facing delivery report (optional)

```bash
python src/generate_client_delivery_report.py
```

Writes an HTML summary under `downloads/reports/` (uses local downloads + patient CSV; keep out of git).

## Privacy / git hygiene

- Credentials, settings, patient lists, `downloads/`, and delivery packages are **gitignored**  
- Do **not** commit real patient CSVs, PDFs, images, or generated HTML reports  
- README and `*.example.yaml` use fictional placeholders only  

## Notes

- Match `facility` in credentials to the portal’s facility dropdown label exactly  
- Long runs need stable network and enough RAM for parallel Chromium workers; lower `worker_count` if the machine swaps or browsers crash  
