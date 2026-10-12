# Executed verification

Date: October 12, 2026.

Command in the generated workspace:

```powershell
$env:PYTHONPATH = (Resolve-Path ../../work/deps).Path
python -m pytest tests -q -p no:cacheprovider --tb=short
```

Result after the separate-portal redesign and legacy importer: **10 passed in 39.57 seconds**. Tests use fresh synthetic databases, never a supplied production database.

Covered: patient and invited doctor registration/login; duplicate and invalid credentials; password hashing; CSRF; logout; profile updates; role restrictions; case submission and input validation; queue isolation; patient ownership and assigned-doctor authorization on cases and original documents; invalid upload type/content and request size; selectable PDF extraction with original text, dates and page sources; scan manual-review fallback; evidence correction; draft visibility restrictions; upload locking after review; finalization gate; doctor-approved patient history; PDF export content; immutable finalized records; audit persistence; reopening the database in another app instance; preservation and backup of an unversioned database; template and static-script routes; CSP; login throttling.

Additional checks cover separate patient/doctor sign-in, server-side portal authorization, staff-ID aliases, read-only legacy import, source/destination snapshots, shared-email accounts across roles, historical note preservation, idempotence and imported-record access restrictions. The version-1 to version-2 user schema migration preserves account IDs and identifier references, passes SQLite foreign-key checks, and creates a backup before changing the table.

JavaScript `node --check static/portal.js` and `node --check static/auth.js`: passed.

Flask server started successfully on `127.0.0.1:5000`; a real HTTP GET returned 200 with the application page and CSP header. Demo accounts and the fictional PDF were generated successfully.

The following full workflow was executed through the in-app browser with fictional records: common landing → patient sign-in → three-step intake → Hindi toggle without losing entered values → submission → synthetic PDF upload → completed text extraction → sign out → separate doctor sign-in → assigned queue → source-linked Hemoglobin/Glucose findings → clinician correction and acceptance → draft summary edit → assessment/advice entry → draft save → finalization → refresh showing Completed → sign out → patient sign-in → approved consultation and clinician-authored advice → successful consultation PDF download. Draft notes persisted through evidence corrections. Landing, patient app and doctor workspace screenshots were captured for visual inspection.

The supplied original database was imported to a separate local `instance/migrated.db`: two accounts and five consultations imported, zero unmatched cases. The original database was opened read-only and backed up; its records and credentials are excluded from version control.

Patient app checked at a 390×844 viewport: no horizontal overflow. The check caught bottom navigation scrolling below the viewport; it was changed to a fixed app navigation bar and rechecked. The browser viewport was restored afterward.

Not verified: successful Tesseract OCR (no OCR engine installed), complex real medical report layouts, production deployment or a comprehensive accessibility audit. The scan fallback was executed and tested.

Dependencies were fetched from PyPI into the workspace's `work/deps` because pip encountered temporary-folder permission issues in this managed environment. The standard virtual-environment commands in README.md remain the portable setup path. The local launcher uses the already installed workspace dependencies.
