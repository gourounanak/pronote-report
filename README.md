# Pronote Weekly Report

Fetches grades from Pronote for all children of a parent account and sends a formatted email every Friday morning.

## Setup

### 1. Install dependencies (local testing)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

> **Note:** Python 3.12+ is recommended. Python 3.9 with LibreSSL causes decryption errors.

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

| Variable | Description |
|---|---|
| `PRONOTE_URL` | URL of your school's Pronote parent page (ends with `parent.html`) |
| `PRONOTE_USERNAME` | Your Pronote username |
| `PRONOTE_PASSWORD` | Your Pronote password |
| `GMAIL_ADDRESS` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | 16-char app password from Google ([how to create one](https://myaccount.google.com/apppasswords)) |
| `EMAIL_TO` | Recipient address(es), comma-separated for multiple |

### 3. Test locally

```bash
python main.py
```

### 4. Deploy to GitHub Actions

1. Push this repo to GitHub (can be private).
2. Go to **Settings → Secrets and variables → Actions**.
3. Add each variable from `.env.example` as a **Repository secret**.
4. The workflow runs every **Friday at 7:00 AM** (Paris time). You may need to enable it first (**Actions** tab → **Weekly Pronote Report** → **Enable** )
   You can also trigger it manually from the **Actions** tab → **Weekly Pronote Report** → **Run workflow**.

## Finding your Pronote URL

Log into Pronote as a parent in your browser. Copy the URL from the address bar — it looks like:

```
https://YOUR_SCHOOL.index-education.net/pronote/parent.html
```

## Email provider

The script sends emails via Gmail SMTP using an [App Password](https://myaccount.google.com/apppasswords). You need 2-Step Verification enabled on your Google account.
