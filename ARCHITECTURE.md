# Architecture

## End-to-end flow

Browser → Flask session/CSRF checks → role and ownership checks → parameterized SQLite transactions → private filesystem reports.

Patient intake → deterministic documentation draft + source-labelled demonstration flags → assigned doctor queue → report source and extracted fields → correction/accept/reject → draft save → finalization gate → published consultation and PDF export.

## Persistence

`users` stores hashed credentials and roles with email uniqueness per role. `cases` stores patient and assigned doctor IDs, self-reported intake JSON, draft/final notes, status, flags and timestamps. `reports` stores private UUID paths and extraction JSON. `findings` preserves original JSON separately from the clinician correction and review decision. `audit` records actor, case, action, before/correction evidence and timestamp. `account_aliases` retains mobile/health/staff identifiers. `legacy_imports` maps historical records idempotently. `schema_version` identifies initialization version 2.

The initializer creates missing tables with `IF NOT EXISTS`. A preexisting database without `schema_version` is copied to `.backup-<timestamp>` before schema setup. Version 2 makes a timestamped backup and transactionally rebuilds the old globally unique-email user table with `(email, role)` uniqueness, preserving all IDs and records. Future changes must increment the version and introduce an explicit transactional migration. `import_legacy.py` explicitly reads and maps the supplied MOA schema into a separate destination with full before/after provenance backups. It never writes to the source.

## Authorization and publication

- A patient can read only their own cases and reports.
- A doctor can read/review only their assigned cases and reports.
- Doctor registration requires a configured private invitation code.
- Report paths are never served from static assets or returned by the API.
- CSRF tokens protect every mutation, including registration and login.
- Cookie sessions have HttpOnly and SameSite=Lax; Secure is configurable for HTTPS.
- User-supplied data is inserted into the UI with `textContent`, never interpreted as HTML.
- CSP allows only same-origin scripts/styles/documents, and excludes executable objects.
- Once review starts, uploads are locked. Finalized notes and findings are immutable.
- Patient APIs redact all draft notes until finalization. Queue APIs omit clinical notes.

Finalization checks that every finding has been accepted, corrected or rejected, requires doctor assessment and recommendations, and requires acknowledgment of flags and original evidence. The evidence workspace maintains original source text and page numbers regardless of corrections. Corrections do not rewrite the original report.

## Extraction and drafting

PyMuPDF handles PDFs; Pillow validates PNG/JPEG content, not just file extensions. Requests are limited to 12 MB, PDF reports to 40 pages, and cases to five reports. UUID file names avoid trusting supplied paths. Encryption or invalid formats are rejected. PDF text is parsed conservatively into candidate numeric laboratory lines. All candidates are unverified; printed reference ranges are copied, not synthesized. The UI presents full original text and document viewing alongside candidates.

Optional Tesseract OCR has a timeout. Missing OCR gives a useful manual-review state with original retained. Selectable PDF extraction does not require OCR. Untrusted reports are data only; no instructions in them execute. Optional, explicit doctor chat context can include selected extracted values, marked as untrusted data. The deterministic intake draft includes missing information and clinician clarification prompts. Doctors can append source-linked report findings after reviewing them.

Demonstration priority rules use the patient's complaint/observations for four explicit phrases (chest pain, difficulty breathing, loss of consciousness, severe bleeding) and mark these for immediate human assessment. Severity ≥8 adds a priority review cue, not an emergency determination. These rules are incomplete, unvalidated, may miss negation/context, and cannot exclude an emergency. Urgent-language banners advise immediate assistance instead of waiting for a queue.


## Multi-branch, speech and assistant extension (2026-10-15)

`clinician_profiles` is an additive table with a foreign key to existing users; missing profiles default to General / unsure. Patient intake JSON stores medical_branch and specialty. Routing selects a doctor in the exact branch; no cross-branch fallback. Existing record ownership does not change. Branch-specific Ayurveda fields are cleared server-side for other branches.

`assistant_service.py` loads local .env settings (process environment wins) and calls only https://api.openai.com/v1/responses with server-side credentials, a timeout, bounded input/output, store:false and sanitized provider errors. `/api/chat` requires login, CSRF, explicit consent, validated conversation roles and language, plus case ownership for doctor-only contextual requests. The in-process per-user limit is six requests/minute. No clinical record is changed by AI; audit retains request metadata only. The model receives no external tools. Provider consent/retention policy and clinical validation remain deployment responsibilities.

`static/experience.js` provides shared localization, browser dictation/read-aloud and an in-memory assistant conversation. Form values and original clinical evidence are never translated. Chat context is opt-in per open doctor case; switching cases clears conversation and invalidates an outstanding response. Microphone permissions and speech-service networking belong to the browser. Database-specific session cookie names avoid cookie collisions across local app copies. Demo scripts use a separate database and port 5015.
