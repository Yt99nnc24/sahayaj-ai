# Updated demo entry point

Double-click start-demo.cmd after installing requirements, then use http://127.0.0.1:5015/. Demo accounts live in a separate database. Both roles use password DemoPassword!2026 and emails patient@example.test / doctor@example.test. Use General / unsure initially, or change the doctor's branch in My profile first. The patient and doctor logins have a Fill demo sign-in control.

Additional checks: choose English/Hindi/Punjabi; verify typed fields remain when switching; use Dictate/Read aloud beneath text boxes in a supported browser. Open Care assistant / Clinical assistant and ask how to upload a report. The Basic offline helper works immediately; run setup-offline.cmd for broader local-model answers. A doctor may separately choose to include the selected case's details. Responses do not update notes or finalize records. No API key is required. See OFFLINE_AI.md for one-time model download and cloud-disable settings.

# Judge demonstration

All data in this walkthrough is fictional. Start with `python backend.py --demo`, then `python backend.py`.

1. Open `http://127.0.0.1:5000`, choose **I’m a patient**, and sign in on the separate patient login page as `patient@example.test` / `DemoPassword!2026`. The patient portal opens with app-style bottom navigation.
2. Select **Start a consultation** or **New visit**. Enter name `Aarav Demo`, age `30`, complaint `Digestive discomfort`, duration `1–3 days`, severity `4`. Continue through the three steps and enter optional self-reported digestion, sleep, Agni and Koshtha observations. Leave Prakriti empty unless qualified assessment exists. Hindi labels can be toggled without clearing entries.
3. Submit the case. It is stored immediately and assigned to the first doctor in the selected branch. Select `demo/synthetic-report.pdf`, then **Upload report**. Wait for the extraction result. Original source lines remain visible; each finding requires manual verification.
4. Refresh. The case and upload persist. Draft clinician notes are hidden from the patient.
5. Sign out, choose **I’m a clinician**, and sign in on the doctor login page as `doctor@example.test` / `DemoPassword!2026`. The desktop clinical workspace has a sidebar queue and separate review panel. Queue counters derive from assigned database cases. Search by name or complaint, or filter by status.
6. Open the case. Compare the original PDF/text and source-linked extracted findings. The synthetic report includes Hemoglobin and Glucose values with printed reference ranges. These are test fixtures, not advice.
7. For each finding choose **accepted**, **rejected**, or enter a correction and choose **corrected**. Inspect the audit record showing original evidence, correction, actor and time (actor ID is persisted in the database).
8. Edit the documentation draft. Optionally choose **Append report evidence to draft** to insert source-linked findings. Add `Fictional clinician assessment for workflow demonstration` and `Fictional clinician-authored advice; no actual treatment recommendation` to the clinician fields.
9. Acknowledge review of flags and original evidence. **Save draft** and refresh to demonstrate persistence. **Finalize & publish to patient**. Pending findings or missing notes block publication.
10. Sign out, return as the patient, open the completed case and read the approved consultation. Choose **Download consultation PDF**. Refresh again to demonstrate persistence.

Optional: submit a second fictional case containing `chest pain` to demonstrate the immediate-human-assessment banner. Explain that flags are incomplete demonstration rules and cannot rule out emergencies. Do not present this as validated triage.

Optional scanned image: upload a PNG/JPG. With no Tesseract it shows `manual_review_required`; the original remains available. Never claim OCR was performed when the manual-review fallback is displayed.
