# Offline assistant verification (2026-10-16)

The paid-provider adapter is replaced by loopback Ollama and bundled no-network guidance. New tests cover basic multilingual answers, unknown/medication questions, urgency bypass, local generation payload, missing-runtime fallback, cloud aliases, redirect/proxy restrictions, and authenticated key-free chat. Existing synthetic workflow/branch/ownership tests remain, with provider contract tests updated.

GitHub Actions completed successfully for cf5d5a3f40a1717ed16b049109b097bafc633cd5: **23 tests passed in 6.17 seconds**, followed by successful syntax checks for all three JavaScript files. Run: https://github.com/Yt99nnc24/sahayaj-ai/actions/runs/38868750007. CI uses synthetic data, basic mode and mocked local-model transport; no model download, real patient data or secrets are used.

After local execution tools recovered, a direct Hindi basic-helper reply was verified. The updated app was started on port 5017; patient demo login and a browser question (How do I upload a report?) produced a labeled Basic offline helper answer with the expected local-model-unavailable notice. No API key or cloud consent was needed. A screenshot was saved locally. Ollama was not running, so no real downloaded-model response is claimed. Model quality, hardware performance and microphone behavior require device testing.

---

## Historical baseline before offline replacement

# Expanded-care verification (2026-10-15)

Latest complete suite: **16 passed** (see command below). The existing clinical workflow and importer checks remain included. Additional checks verify exact-branch clinician routing, unavailable/invalid branches, Ayurveda-only fields cleared on other branches, doctor profile branch updates, and ownership restrictions.

Assistant checks: login/CSRF, explicit consent, bounded roles/messages/language, patient context exclusion, doctor case ownership, missing-key response, injected-provider request/response, unchanged notes/status, metadata-only audit, per-user throttling, Responses API store:false payload, configured model, and sanitized provider errors. No real OpenAI request was made: no API key was supplied. The transport contract and UI failure path were tested using synthetic data/mocked responses.

Demo initializer executed twice on a fresh isolated database: both patient and doctor credentials logged in successfully and no duplicate accounts were created. Environment loading and process-variable precedence tested. Different databases receive distinct session cookie names.

Browser executed on the updated app at port 5015: doctor demo login; assistant consent gate and clear missing-key response; Punjabi doctor controls; patient demo login; intake language switching preserves complaint, branch and age; all medical branch choices; Allopathy hides Ayurveda fields and Ayurveda shows them; General / unsure intake submitted and appears in doctor queue; doctor summary/assessment/advice dictation controls and contextual assistant visible. Patient Punjabi intake checked at 390x844: document width 375, no horizontal overflow, fixed navigation bottom at 844. Doctor desktop workspace inspected at 1280x900. Temporary viewport restored.

`node --check` passed for auth.js, portal.js and experience.js; Python modules compile.

Not live-verified: microphone recording/transcription, OS speech voices or successful OpenAI generation with a billed key. Browser/OS permissions and voices must be checked on the user's device. English/Hindi/Punjabi cover core interface controls; explanatory/technical copy and original clinical records remain English/original. No production/clinical validation implied.

Full test command from repository directory:

```powershell
python -m pytest tests -q -p no:cacheprovider
```

---

## Previous baseline (2026-10-12)

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
