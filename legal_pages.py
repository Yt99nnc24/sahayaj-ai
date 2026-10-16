"""Public notices describing this installation's actual features and limits."""
PAGES = {
 'privacy': {
  'title':'Privacy Policy', 'eyebrow':'YOUR INFORMATION',
  'intro':'A clear explanation of what Sahayaj stores, why it is needed, and the choices available to you.',
  'summary':'Your consultation belongs in a care conversation. We do not use advertising trackers or send your chat to a paid AI service.',
  'sections':[
   ('responsibility','Who is responsible',[
    'Your clinic, or the person operating this installation, is responsible for the information you share here. Contact that operator for privacy questions or requests. This notice describes the current local demonstration; a clinic using a hosted version must identify its operator and explain its own processing arrangements.']),
   ('information','Information you provide',[
    'Account information includes your name, email address, patient or staff identifier if supplied, role, and a hashed password. We do not store your password as plain text.',
    'Consultation information includes the symptoms, health history, medicines, allergies, medical branch and other details you enter, uploaded reports, extracted report findings, clinician notes, review decisions and consultation history.',
    'The application also records timestamps and an audit trail for record changes and assistant requests. Assistant audit entries contain request metadata, not the conversation text. The development server may log request paths, response codes and connection information.']),
   ('purpose','How information is used',[
    'Information is used to sign you in, connect a consultation to an assigned clinician, present original evidence for review, maintain continuity and traceability, and provide a consultation PDF. A clinician must review and approve medical notes; the assistant does not finalize them.',
    'Your medical branch selection is used for workflow routing. It is not professional credential verification or an endorsement of every treatment offered within a branch.']),
   ('access','Who can access it',[
    'The application limits patient records to the patient and the assigned clinician. The person administering the computer or server may also access the underlying files and backups. Shared computers and administrator accounts therefore require care.',
    'We do not include advertising, analytics trackers or a sale-of-data feature. If an operator adds services, shares records outside this application or hosts it for others, they must explain those arrangements separately.']),
   ('assistant','Chat and voice features',[
    'Typed chat uses a bundled basic helper or a downloaded model served by Ollama on the same computer as the application server. The application has no hosted AI fallback. The interface labels which mode answered.',
    'Chat messages are held in page memory and cleared on reload, a new conversation or a change of consultation. Local model software can retain a model in memory and may have its own operational logs. The application does not save a conversation transcript to the clinical database.',
    'A doctor can choose to include the open consultation in the assistant request. The name field is excluded, but free-text entries can still contain identifying information. Patient records are not automatically attached to patient chat.',
    'Voice dictation is optional. It starts only when you press the microphone control and your browser permits microphone access. The browser or operating-system speech service may process audio online under its own policy. Use typed chat if you want to avoid that service.']),
   ('storage','Storage and retention',[
    'Accounts, consultations and audit records are stored in the configured local database. Reports and backups are stored in the installation’s private folders. They remain until the operator removes them; this version does not implement automatic retention periods or a self-service account deletion flow.',
    'Request access, correction, export or deletion from the operator. The operator should explain any clinical, recordkeeping or legal reasons that affect what can be changed or deleted, and how copies in backups are handled. Clearing browser cookies does not delete clinical records.']),
   ('security','Protecting your information',[
    'The application uses password hashing, signed sessions, request protections and checks on record access. These controls do not make a development installation a production medical-record service. Files are not encrypted at rest by this application, and local HTTP connections are not encrypted in transit.',
    'Use the fictional demo data for evaluation. A real deployment needs suitable hosting, HTTPS, access management, backups, security review and a retention policy appropriate to its operation.']),
   ('choices','Your choices and requests',[
    'You can choose what optional details to provide, decline microphone access, type instead of using voice, clear a conversation, sign out, or reset display preferences. Essential session storage is needed for authenticated features.',
    'For requests relating to stored information, contact your clinic or the installation administrator. They should verify your identity without asking you to send your password. Depending on the law that applies to your operator, additional information rights and a right to raise concerns with a regulator may be available.']),
   ('updates','Changes to this notice',[
    'This notice may change when the service’s features or handling of information changes. The revision date appears at the top of this page. Material changes should be brought to users’ attention by the operator.'])]},
 'cookies': {
  'title':'Cookie Policy', 'eyebrow':'BROWSER STORAGE',
  'intro':'A small amount of browser storage keeps your session working and remembers the display choices you make.',
  'summary':'No advertising cookies. No analytics trackers. Session security and the preferences you choose are described below.',
  'sections':[
   ('essential','Session cookies',[
    'A first-party cookie with a name beginning sahayaj_ carries the signed session used for sign-in and request protection. It is set when the application establishes a session, including before login to protect forms. Blocking it prevents authenticated features from working.',
    'It is a browser-session cookie. Browsers that restore a previous session can keep session cookies across a restart. Signing out clears the application session. Its contents are signed to detect modification, not encrypted.']),
   ('preferences','Display preferences',[
    'Local storage remembers the interface language and the patient or doctor theme selected on this browser. These entries are not cookies and do not travel with every web request. They remain until you reset them or clear site data.',
    'This version does not store chat transcripts in cookies or local storage. Preferences do not contain your consultation history.']),
   ('controls','Managing storage',[
    'Your browser settings let you view or remove cookies and local storage, block site storage, and manage microphone permissions. Removing essential session storage signs you out or requires you to refresh a form.',
    'The Reset display preferences control below removes only Sahayaj’s saved language and theme choices. It does not delete your account, medical records, reports or essential session cookie.']),
   ('third-parties','Other services',[
    'This application does not embed third-party analytics, advertising, social widgets or remote fonts. Installing or downloading a local model is a separate setup step. Browser speech recognition may contact the browser vendor’s service when you explicitly use dictation.',
    'If an operator adds non-essential tracking or another external service, this notice and any required choice mechanism must be updated before that service is used.'])]},
 'terms': {
  'title':'Terms & Conditions', 'eyebrow':'USING SAHAYAJ',
  'intro':'The purpose of this service, the responsibilities of its users, and the limits of its automated features.',
  'summary':'Sahayaj helps organize care information. It does not replace a qualified clinician or an emergency service.',
  'sections':[
   ('scope','About the service',[
    'Sahayaj provides patient intake, report organization, a clinician review workspace and an optional local assistant. This version is a demonstration for evaluation with fictional data. It is not clinically validated software or a substitute for a properly operated medical service.',
    'These terms describe use of the application. They do not create a patient–clinician relationship, replace a clinic’s consent process, or replace any separate agreement you have with your care provider.']),
   ('care','Medical and emergency limits',[
    'Do not rely on this application to decide whether an emergency exists. Seek immediate in-person medical assistance for urgent symptoms rather than waiting for a chat response or review queue.',
    'Automated summaries, extracted report values and assistant replies can be incomplete or incorrect. They are not diagnoses, prescriptions or instructions to change treatment. A qualified clinician must independently assess the patient and verify source evidence.',
    'Support for different medical branches is a workflow feature. It does not establish that all treatments are effective, appropriate or supported by the same level of evidence.']),
   ('accounts','Accounts and responsible use',[
    'Provide information you are entitled to share and keep your sign-in details private. Use your own account and sign out on shared devices. Do not upload another person’s information without appropriate permission or authority.',
    'Do not impersonate a clinician, attempt to access another person’s records, bypass safeguards, upload malicious files, or interfere with the service. A doctor invitation code is an access control, not verification of a professional licence.',
    'A minor or a person who needs assistance should use the service with an appropriately authorized adult and in accordance with the clinic’s process and applicable requirements.']),
   ('clinicians','Clinician responsibilities',[
    'Clinicians remain responsible for working within their professional scope, checking original reports, clarifying missing history, making clinical decisions and reviewing what they publish. Suggestions must not be copied into care instructions without independent review.',
    'Finalized records are locked in this version. Contact the operator if a correction is needed; do not assume that editing a separate chat corrects a medical record.']),
   ('ai','Assistant and availability',[
    'The basic offline helper offers limited fixed guidance. A downloaded local model can answer broader questions but may invent or misinterpret information. The provider label identifies the mode used; neither mode is a verified medical expert.',
    'Features may be interrupted, unavailable or incompatible with a browser or device. Local model speed and language quality vary with hardware and model. There is no guarantee of uninterrupted availability or of any medical outcome.',
    'The application does not charge for a hosted AI API. Local model installation may require downloads, disk space, hardware resources and agreement to the model or runtime provider’s own terms.']),
   ('privacy','Your information',[
    'Read the Privacy Policy and Cookie Policy to understand stored information, local inference, optional browser speech services and retention. The operator is responsible for its deployment arrangements and for responding to information requests.']),
   ('changes','Changes and questions',[
    'Features and these terms may be updated. The operator should explain material changes before users rely on them. For questions, access problems, privacy requests or a concern about a record, contact your clinic or the person operating this installation.',
    'Nothing in these terms is intended to exclude rights or responsibilities that cannot lawfully be excluded under the law that applies to you and your operator.'])]}
}
