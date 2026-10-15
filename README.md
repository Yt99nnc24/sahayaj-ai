# SAHAYAJ AI

Connected clinical workflows across medical branches.

A local Flask + SQLite multi-branch care demonstration with a common landing page, separate patient and doctor login pages, an app-style patient portal and a desktop clinical workspace. Includes patient intake, private reports, deterministic extraction, evidence review, clinician drafts, finalization and PDF consultation downloads. The optional OpenAI chatbot sends only explicitly approved conversation/context to OpenAI; report extraction remains local.


## Quick demo (Windows CMD or double-click)

After installing requirements once, double-click **start-demo.cmd**. It prepares `instance/demo.db` and serves **http://127.0.0.1:5015/**. This isolates fictional demo accounts from clinic/imported records and avoids older servers on ports 5000/5001. Keep the terminal open. If port 5015 is occupied, stop the older demo terminal with Ctrl+C first. The login page now reports whether demo accounts exist.

- Patient: `patient@example.test`
- Doctor: `doctor@example.test`
- Both passwords: `DemoPassword!2026`

No invitation code is needed to sign in. The demo doctor initially handles **General / unsure**. To test Ayurveda, Allopathy, Homeopathy, Unani, Siddha, Naturopathy/yoga, Dental or Other, sign in as the doctor, choose **My profile → Medical branch → Save profile**, then select that same branch in the patient intake. Existing cases stay with their assigned doctor. Specialty/problem is recorded as patient context, not automatic specialist credential verification. Ayurveda's Agni/Koshtha/Prakriti fields appear only for Ayurveda.

## OpenAI chatbot setup

Copy `.env.example` to `.env` beside `backend.py`. Edit it in Notepad (never publish this file):

```dotenv
OPENAI_API_KEY=your-own-api-key
OPENAI_MODEL=gpt-4.1-mini
SAHAYAJ_DOCTOR_CODE=your-own-private-registration-code
SAHAYAJ_SECURE_COOKIE=0
```

Restart the server. `start.cmd` launches the regular database; `start-demo.cmd` launches the fictional database. The same `.env` settings are loaded by both. ChatGPT subscription access does not supply this application's API credentials. Configure a model available to your API project; API usage requires your own account/billing.

Open **Care assistant** or **Clinical assistant**. Agree to sending the conversation before sending a question. Doctors can separately opt in to include the open consultation's intake and extracted findings; names are excluded but free text can still identify a person. Patient chat does not automatically receive records. No file uploads, raw report files, key, full name or email are added automatically to OpenAI prompts. Chats stay in page memory and clear when navigating between cases or reloading. Request metadata (role/language/context inclusion), not conversation content, is audited. Requests use the [OpenAI Responses API](https://developers.openai.com/api/docs/guides/text) with `store:false`; this is not a guarantee of zero provider retention. See [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data).

Responses are unverified educational/checklist suggestions, not diagnoses or prescriptions. All medical branches are supported as workflow categories; this does not imply equal evidence for treatments. No tools, browsing, autonomous prescriptions or automatic note publication are enabled. Without a key, the UI displays setup instructions and makes no outbound model call.

## Voice and languages

Use **Dictate** beneath patient intake, doctor note and chat text boxes. Click again to stop; review the resulting text before saving. **Read aloud** reads text with the selected interface language; **Stop reading** cancels playback. Speech uses browser Web Speech APIs, not OpenAI audio. Microphone permission and recognition/voice availability depend on the browser, OS and selected language; Chrome/Edge are recommended for recognition. Your browser's recognition service may process audio online. No audio is stored by this app. If unsupported or denied, a clear message is shown and typing remains available. Closing/hiding the page stops speech.

Language selector: English, हिन्दी, ਪੰਜਾਬੀ. Core labels and navigation are localized; medical records are not translated or overwritten, and additional explanatory copy currently remains English. Language-specific dictation and assistant replies follow the selected language.

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

Open <http://127.0.0.1:5000>. The application automatically loads literal `KEY=value` settings from the project `.env` file; existing process environment variables take precedence. Keep the same secret between restarts to retain sessions. If no secret is configured, a generated local key is persisted under `instance/session.key`.

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

OCR runs only if both `pytesseract` and the separate Tesseract executable are installed and on PATH; it is always marked for manual verification. Without OCR, scanned PDFs and images remain privately available with a manual-review status. OCR confidence scoring is not implemented; all OCR content is treated as unverified. The editable intake draft remains deterministic. Optional OpenAI chat is separate and never changes/finalizes records. English, Hindi and Punjabi are selectable on public, login and both portal pages for core navigation/forms; technical explanations and clinical evidence retain their original text. Language switching preserves typed fields and canonical values. Both portals support a saved dark theme preference.

Cases are assigned to the first registered doctor in the requested medical branch. Existing accounts without a branch are treated as General / unsure. A branch without a clinician produces a clear error instead of cross-branch assignment. Other doctors cannot access them. Multi-clinic routing, reassignment, professional verification, account recovery, malware scanning, encryption at rest, managed backups and multi-worker rate limits are future work. The login throttle is in-process. Private storage depends on local OS account permissions. Do not put this development server on a public network or use it for actual medical records. Production requires HTTPS, secure cookies (`SAHAYAJ_SECURE_COOKIE=1`), a WSGI server and operational security review.

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
