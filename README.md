# Company Information Bulk Export

Browser-based automation that bulk-exports **customer records from a company portal** into a clean, per-customer folder package. It logs in, selects the company, walks your customer list, and downloads the same files and histories a staff member would open one customer at a time—without requiring direct database access.

## Authorized use

This tool is for **authorized operators only**. Use it only when you have permission to access and export the data for a legitimate business purpose (for example migration, handoff, or an approved archive).

- Do **not** use this against systems or accounts you are not authorized to access.
- Exported files can contain **confidential customer and company information**. Treat them as sensitive business records.
- Keep credentials, customer lists, and `downloads/` **off git** and share packages only through approved channels.
- You are responsible for complying with your organization’s policies and applicable privacy laws.

## Why this exists (when a database export is not enough)

Many migrations, audits, and handoffs need **the records as users actually see them in the portal**—not only rows in tables.

A SQL / DB dump often falls short because:

| What you need | Why the DB alone is awkward |
|---|---|
| **Rendered documents (PDFs)** | Final documents are usually generated views or stored files—not a single readable column. |
| **Images and media** | Binary assets live behind the UI or object storage—not CSV-friendly. |
| **Threaded message / activity history** | Conversation and activity UIs may be incomplete, encoded, or split across services in raw tables. |

This automation is helpful when you need a **faithful, customer-by-customer file package** for:

- Company migration or portal cutover
- Client delivery of historical records
- Compliance / audit archives where documents and images matter
- Cases where you have **portal access** but not a practical bulk-document API or DB map

It does **not** replace a warehouse for analytics. It complements (or substitutes for) DB export when the deliverable is **documents + readable histories**.

## What this automation delivers

For every customer in the input list, it builds a numbered folder tree under:

```text
downloads/<Company Name>/{CustomerId}_{FirstName}_{LastName}/
├── 01_…/   → profile / details export
├── 02_…/   → images
├── 03_…/   → appointment / schedule history
├── 04_…/   → service history
├── 05_…/   → document PDFs (as available in the portal)
├── 06_…/   → additional document PDFs (as available)
├── 07_…/   → invoice PDFs
├── 08_…/   → membership / subscription invoice PDFs
├── 09_…/   → credits CSV
└── 10_…/   → message log CSV
```

Exact folder labels follow the portal categories configured in the automation. Reviewers do not need the internal category map—operators see the full tree in their local `downloads/` after a run.

Also produced after runs:

- **Execution / progress HTML reports** under `downloads/reports/`
- **Client delivery HTML** via `python src/generate_client_delivery_report.py`
- **Run logs** under `downloads/logs/` (and optional supervised overnight log)

Built for large companies: **resume** (skip finished categories), **Phase 1 incomplete → Phase 2 new customers**, multi-worker browsers, and an optional **supervisor** that auto-restarts and backs off workers on memory/browser crashes.

## What input it needs

| Input | Required | Description |
|---|---|---|
| Customer list CSV | **Yes** | Columns: `id`, `first_name`, `last_name` (extra columns OK). Place in the **project root** (same folder as this README). |
| `config/credentials.yaml` | **Yes** | Portal username, password, and **exact** company label from the portal dropdown. Copy from `config/credentials.example.yaml`. **Not committed.** |
| `config/settings.yaml` | **Yes** | Portal URL, browser mode, timeouts, workers, optional supervisor. Copy from `config/settings.example.yaml`. **Not committed.** |

CSV selection on startup:

1. Scans the project root for valid customer CSVs
2. If several exist, prefers a filename matching the company name from credentials; otherwise newest file
3. Writes under `downloads/<Company Name>/`

## Backend / tools required to set it up

This is a **local automation client**, not a hosted backend service. You need:

| Requirement | Purpose |
|---|---|
| **Python 3.8+** | Runtime |
| **pip** + `requirements.txt` | Installs `playwright`, `pyyaml`, `aiofiles` |
| **Playwright browsers** (`playwright install`) | Chromium to drive the portal UI — **required**; pip alone is not enough |
| **Network access** to the company portal | Login + downloads |
| **Valid portal user** with rights to open customers and export their documents/histories | Same permissions a staff export would need |
| **Disk space** | Document/image-heavy companies can be tens of GB |
| **OS** | Windows / macOS / Linux where Playwright is supported |

### Setup (do this in order)

```bash
git clone https://github.com/Tamzida-Azad/Information-Bulk-Export.git
cd Information-Bulk-Export

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

Edit `config/credentials.yaml` and `config/settings.yaml`, then place a customer CSV in the project root.

### Common setup failures (and fixes)

| Symptom | Likely cause | Fix |
|---|---|---|
| `FileNotFoundError` for `credentials.yaml` / `settings.yaml` | Examples not copied | Copy `*.example.yaml` → `credentials.yaml` / `settings.yaml` |
| Browser / Playwright errors on first run | Browsers not installed | Run `playwright install chromium` |
| Company not found in portal select | Company string ≠ portal dropdown | Copy the label exactly (spaces, dashes, casing) |
| `No patient list CSV found` / no customer CSV | CSV missing or wrong columns | Put CSV in project root with `id`, `first_name`, `last_name` |
| Workers crash / MemoryError overnight | Too many browsers for RAM | Lower `worker_count` (e.g. 5→3→2) or use `watch_export.py` |
| Login failed | Bad credentials or portal URL | Check username/password and `base_url` in settings |

## What data is pulled (high level)

Per customer, the automation exports whatever categories the portal exposes for that account—typically a mix of:

- Profile / contact details (CSV)
- Images
- Schedule and service history (CSV)
- Document and invoice PDFs
- Credits and message history (CSV)

Operators see the concrete folder names and file naming after a local run. This README intentionally stays high-level so public reviewers are not given a portal-specific data dictionary.

## Run

```bash
python src/main.py
```

- Finished customers (all categories done) are skipped unless newer portal records are detected
- Incomplete customers are finished first (**Phase 1**), then not-yet-started customers (**Phase 2**)

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

Writes an HTML summary under `downloads/reports/` (uses local downloads + customer CSV; keep out of git).

## Privacy / git hygiene

- Credentials, settings, customer lists, `downloads/`, and delivery packages are **gitignored**
- Do **not** commit real customer CSVs, PDFs, images, or generated HTML reports
- README and `*.example.yaml` use fictional placeholders only

## Notes

- Match the company name in credentials to the portal’s company dropdown label exactly
- Long runs need stable network and enough RAM for parallel Chromium workers; lower `worker_count` if the machine swaps or browsers crash
