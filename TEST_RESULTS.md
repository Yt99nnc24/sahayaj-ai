# Executed verification

Date: October 12, 2026.

Command in the generated workspace:

```powershell
$env:PYTHONPATH = (Resolve-Path ../../work/deps).Path
python -m pytest tests -q -p no:cacheprovider --tb=short
```

Result after the separate-portal redesign and legacy importer: **9 passed in 56.93 seconds**. Tests use fresh synthetic databases, never a supplied production database.

Covered: patient and invited doctor registration/login; duplicate and invalid credentials; password hashing; CSRF; logout; profile updates; role restrictions; case submission and input validation; queue isolation; patient ownership and assigned-doctor authorization on cases and original documents; invalid upload type/content and request size; selectable PDF extraction with original text, dates and page sources; scan manual-review fallback; evidence correction; draft visibility restrictions; upload locking after review; finalization gate; doctor-approved patient history; PDF export content; immutable finalized records; audit persistence; reopening the database in another app instance; preservation and backup of an unversioned database; template and static-script routes; CSP; login throttling.

Additional checks cover separate patient/doctor sign-in, server-side portal authorization, staff-ID aliases, read-only legacy import, source/destination snapshots, shared-email accounts across roles, historical note preservation, idempotence and imported-record access restrictions.

JavaScript `node --check static/portal.js` and `node --check static/auth.js`: passed.

Flask server started successfully on `127.0.0.1:5000`; a real HTTP GET returned 200 with the application page and CSP header. Demo accounts and the fictional PDF were generated successfully.

Browser access subsequently connected and the common landing page was checked through its rendered accessibility state. Full browser workflow and screenshot verification are recorded only if completed; automated backend verification already executes file upload, correction, clinician publication, patient retrieval and PDF download.

The supplied original database was imported to a separate local `instance/migrated.db`: two accounts and five consultations imported, zero unmatched cases. The original database was opened read-only and backed up; its records and credentials are excluded from version control.

Not verified: successful Tesseract OCR (no OCR engine installed), complex real medical report layouts, production deployment, accessibility audit or mobile-browser visual behavior. The scan fallback was executed and tested.

Dependencies were fetched from PyPI into the workspace's `work/deps` because pip encountered temporary-folder permission issues in this managed environment. The standard virtual-environment commands in README.md remain the portable setup path. The local launcher uses the already installed workspace dependencies.
