# Policy pages and chatbot interface

Public pages: `/privacy`, `/cookies` and `/terms`. Descriptive aliases redirect to the canonical pages. Policy links are available from landing, sign-in and both authenticated portals. The notices describe this local demonstration and the features actually implemented: hashed passwords, signed session cookies, browser preference storage, records/backups, optional browser speech, loopback AI, and metadata-only assistant auditing.

The notices do not claim GDPR, DPDP, HIPAA or other legal certification. Before using this project as a real hosted clinic service, the operator must identify itself, provide a direct privacy contact, establish actual retention/security arrangements and review the notices for its jurisdiction and operation. No fake company address, compliance badge or invented contact is included. Policies currently appear in English.

The cookie page distinguishes the essential session cookie from language/theme local storage and offers a reset control scoped to those display preferences. It does not delete medical records or sign the user out. There are no advertising/analytics integrations or non-essential tracking toggles to pretend to control.

The chatbot is now a separate component in `static/chatbot.js` and `static/chatbot.css`. It uses explicit user/assistant bubbles, suggested questions, message-level copy/read actions, a compact composer, a local/basic mode indicator, loading and retry states, and language-aware controls. Case switches abort a pending response and clear context. Conversations remain in page memory. DOM text nodes are used for replies; model text is never interpreted as HTML.

Background guidance on clear privacy and storage information: [ICO privacy notices and cookies](https://ico.org.uk/for-organisations/advice-for-small-organisations/privacy-notices-and-cookies/cookies-and-privacy-notices-in-detail/). This is a transparency reference, not a statement that UK law governs this installation.
