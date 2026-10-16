# Original project inspection and upgrade checklist

Inspected all six supplied files under `C:/Users/Admin/Desktop/MOA` and the database schema in read-only mode. The three HTML files are also duplicated in `templates/`; those copies match the supplied file lengths. The original folder and original database are never edited by this upgrade.

## Existing strengths retained

- Separate patient and doctor workflows and a shared SQLite backend.
- Patient tablet-style interface, quick complaint choices, Agni and Koshtha observations, diet selection and Hindi/English intake controls.
- Doctor sidebar queue, patient overview and prior visit history.
- Password hashing and parameterized SQL in the original backend.

## Repairs and design changes

- Common landing page routes to two separate sign-in pages, then two distinct portal layouts.
- Patient experience uses an app shell, bottom navigation, three-step intake, report uploads and consultation history cards.
- Doctor experience uses a desktop sidebar, database queue, original report viewing, source-linked findings and a separate review panel.
- Authentication moves from sessionStorage-only identity to server-side session cookies and CSRF tokens.
- Every case/report endpoint checks patient ownership or assigned doctor access.
- Original unauthenticated queue/history/update endpoints are not exposed.
- Original HTML inserted untrusted records/chat input through innerHTML; the new UI uses textContent for dynamic content.
- Hardcoded automatic diagnoses, medications and dosages are removed; documentation assistance is evidence-based and clinician controlled.
- Original static doctor identity is replaced with the signed-in account name.
- Original success alerts ignored HTTP error status; new clients check server responses and show actionable failures.
- Changing intake language no longer resets entered field values.
- Finalization is explicit, blocked by unreviewed findings, and records an audit event.

## Database preservation

The original database has one patient, one doctor and five intake records. Names, identifiers, clinical details and password hashes are not printed in inspection output and are excluded from Git.

`import_legacy.py` reads the original SQLite file in read-only mode, makes a full snapshot of it and the destination before writing, preserves password hashes, adds mobile/health/staff ID login aliases, maps historical records and records import provenance. Repeated imports skip previously mapped records. Unmatched records remain in the full backup rather than being assigned to an arbitrary patient. Email collisions abort the import transaction. Legacy cases had no doctor ID: a sole legacy doctor is used or an explicit `--doctor-email` is required. Imported historical advice is preserved verbatim and is not newly verified or regenerated.

## Remaining boundaries

As of 2026-10-15, explicit browser dictation and read-aloud controls are available in both portals with permission/fallback messages. English/Hindi/Punjabi core controls preserve original record text. Optional OpenAI conversation requires explicit consent; doctor context has a separate opt-in and ownership check. OCR engine installation remains optional. Source changes are published using the authenticated GitHub connector.


2026-10-16 update: the optional OpenAI feature described above has been replaced by local-only Ollama plus a labeled bundled offline helper. No API key or paid model service is used. See OFFLINE_AI.md for setup and current limits. Other preserved clinical workflows and original-record backups are unchanged.
