# SAHAYAJ AI

Bridging Ancient Ayurvedic Wisdom with Intelligent Clinical Workflows.

A local Flask + SQLite Ayurveda OPD demonstration with a common landing page, separate patient and doctor login pages, an app-style patient portal and a desktop clinical workspace. Includes patient intake, private reports, deterministic extraction, evidence review, clinician drafts, finalization and PDF consultation downloads. No paid API or third-party medical data transmission is used.

## Windows / VS Code setup

Open this `sahayaj-ai` directory in VS Code. In its PowerShell terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
$env:SAHAYAJ_SECRET = (python -c "import secrets; print(secrets.token_hex(32))")
$env:SAHAYAJ_DOCTOR_CODE = 'choose-a-private-doctor-invitation-code'
$env:SAHAYAJ_SECURE_COOKIE = '0'
python backend.py --init
python backend.py --demo
python backend.py
```

Open <http://127.0.0.1:5000>. Flask does **not** automatically load `.env`: either set the PowerShell variables shown above on each new terminal session or configure them in VS Code's launch environment. Keep the same secret between restarts to retain sessions. If no secret is configured, a generated local key is persisted under `instance/session.key`.

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` in place of `python`; activation is optional.

Run automated tests:

```powershell
python -m pytest tests -q -p no:cacheprovider
```

For the current generated workspace only, installed dependencies are available in `../../work/deps`; `./run-local.ps1` uses them and starts the server without installing again. On another computer use the virtual environment setup above.

## Demo credentials

Run `python backend.py --demo` to create accounts without replacing existing users:

| Role | Email | Password |
| --- | --- | --- |
| Patient | patient@example.test | DemoPassword!2026 |
| Doctor | doctor@example.test | DemoPassword!2026 |

The generated `demo/synthetic-report.pdf` is explicitly fictional. Use these accounts only for a local demonstration.

## Files

- `backend.py`: API, schema initialization, authorization, extraction, priority rules, audit and export.
- `templates/landing.html`, `templates/login.html`, `templates/portal.html`: common entry, separate sign-in and distinct portal layouts.
- `static/design.css`, `static/auth.js`, `static/portal.js`: design system, authentication and connected workflows.
- `import_legacy.py`: read-only legacy import with source/destination backups, account aliases and record mapping.
- `tests/`: synthetic workflow and security checks.
- `data.py`: schema and counts; does not print medical records.
- `ARCHITECTURE.md`, `DEMO_GUIDE.md`, `TEST_RESULTS.md`: operation and verification details.
- `instance/`: runtime SQLite database, secret and private reports; excluded from Git.

## Limits and deployment boundary

This is a hackathon prototype, not clinically validated software. Priority rules are demonstrations, cannot rule out emergencies, and do not provide a diagnosis or prescription. All advice is authored and finalized by the doctor. Physician registration requires an invitation code, not verified professional licensing.

PDF extraction supports selectable text and simple one-line numeric laboratory entries. Dates, printed units, ranges, page numbers and source lines are retained; absent values/ranges are not inferred. Complex columns, qualitative tests, handwriting and broken text order require manual review. Every finding requires a review decision. A doctor must acknowledge original evidence and flags before finalizing, including documents without extractable findings.

OCR runs only if both `pytesseract` and the separate Tesseract executable are installed and on PATH; it is always marked for manual verification. Without OCR, scanned PDFs and images remain privately available with a manual-review status. OCR confidence scoring is not implemented; all OCR content is treated as unverified. No LLM is integrated; the editable draft is deterministic and identifies its intake sources. Patient navigation and intake labels support Hindi without clearing form values; clinical evidence and canonical option values remain English. Both portals support a saved dark theme preference.

Cases are assigned to the first registered doctor. Other doctors cannot access them. Multi-clinic routing, reassignment, professional verification, account recovery, malware scanning, encryption at rest, managed backups and multi-worker rate limits are future work. The login throttle is in-process. Private storage depends on local OS account permissions. Do not put this development server on a public network or use it for actual medical records. Production requires HTTPS, secure cookies (`SAHAYAJ_SECURE_COOKIE=1`), a WSGI server and operational security review.

The original MOA files have now been inspected. See `INSPECTION.md` for preserved functionality, security repairs and schema findings. The original folder is not modified. Real records, database copies and credentials are excluded from Git.

## Import the original MOA database safely

Run from this project directory after installing dependencies. This creates a separate database and preserves the source:

```powershell
python import_legacy.py "C:\Users\Admin\Desktop\MOA\database.db" --target instance\migrated.db
$env:SAHAYAJ_DATABASE = (Resolve-Path instance\migrated.db).Path
python backend.py
```

Imports preserve patient mobile/health ID and doctor staff ID login, existing password hashes and historical notes. Emails can be shared across patient and doctor roles; each login page selects the correct role. Repeated imports are idempotent. Full source and destination snapshots are stored in `instance/backups/`. With multiple legacy doctors, pass `--doctor-email` to select ownership explicitly. Existing same-role email collisions abort the transaction; do not overwrite users. Historical records with unknown patient identifiers are retained in the backup and reported as unmatched.

To return to the synthetic demo database, stop the server and run `Remove-Item Env:SAHAYAJ_DATABASE -ErrorAction SilentlyContinue`, then `python backend.py`.
