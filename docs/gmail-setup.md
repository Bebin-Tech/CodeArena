# Gmail verification email setup

A domain is not required when CodeArena sends from a Gmail mailbox. Gmail SMTP uses `smtp.gmail.com`, port `587`, and STARTTLS. The From address must match the authenticated mailbox. CodeArena verifies Google's TLS certificate before authenticating.

## Google account

1. Enable [2-Step Verification](https://myaccount.google.com/signinoptions/two-step-verification).
2. Open [App Passwords](https://myaccount.google.com/apppasswords) and create one named CodeArena.
3. Keep that password private. Use it instead of your normal Google password. Some managed accounts and accounts with certain security settings do not offer App Passwords; see [Google's account requirements](https://support.google.com/accounts/answer/185833).

## Vercel production settings

In the CodeArena project's [environment settings](https://vercel.com/bebin-dotms-projects/codearena/settings/environment-variables), configure:

| Key | Value |
| --- | --- |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_STARTTLS` | `true` |
| `SMTP_USERNAME` | Your full Gmail address |
| `MAIL_FROM` | `CodeArena <your-address@gmail.com>` |
| `SMTP_PASSWORD` | Google App Password, stored as a Production Secret/Sensitive variable |

Store the password only in Vercel; do not paste it into chat, commit it, or put it in a command-line argument. Google displays App Passwords with spaces; CodeArena removes that display spacing before SMTP login. Gmail credentials never fall back to a Resend API key.

Redeploy after changing environment variables. The `/api/v1/auth/providers` response reports `email: true` once the required settings are present; that flag reports configuration readiness, not proof of inbox delivery.

## Connection check

From a checkout linked to the correct Vercel project:

```powershell
npm.cmd exec --yes --package=vercel@66.2.0 -- vercel project inspect --non-interactive
npm.cmd exec --yes --package=vercel@66.2.0 -- vercel env run -e production -- .venv\Scripts\python.exe scripts\check-smtp.py
```

This verifies TLS and SMTP authentication and sends no email. If Vercel does not inject protected production secrets into local commands, use the deployed app to test registration instead; do not copy the secret into local files. Open the verification email in Gmail (check Spam if needed), verify once, then sign in. Password recovery uses the same sender and SMTP connection.

Gmail is suitable for an initial small deployment but is subject to account sending limits and anti-abuse controls. It is not an unlimited transactional email service. Changing your Google password can revoke App Passwords; replace the Vercel secret and redeploy if that occurs.

References: [Google SMTP documentation](https://developers.google.com/workspace/gmail/imap/imap-smtp), [Google App Passwords](https://support.google.com/accounts/answer/185833).
