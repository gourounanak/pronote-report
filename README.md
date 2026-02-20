# Pronote Weekly Report

Fetches grades from Pronote for all children of a parent account and sends a formatted report every Friday morning via email and/or WhatsApp.

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

| Variable | Description | Required |
|---|---|---|
| `PRONOTE_URL` | URL of your school's Pronote parent page (ends with `parent.html`) | Yes |
| `PRONOTE_USERNAME` | Your Pronote username | Yes |
| `PRONOTE_PASSWORD` | Your Pronote password | Yes |
| `GMAIL_ADDRESS` | Your Gmail address | For email |
| `GMAIL_APP_PASSWORD` | 16-char app password from Google ([how to create one](https://myaccount.google.com/apppasswords)) | For email |
| `EMAIL_TO` | Recipient address(es), comma-separated for multiple | For email |
| `META_ACCESS_TOKEN` | WhatsApp Business API access token from Meta | For WhatsApp |
| `META_PHONE_NUMBER_ID` | WhatsApp Business phone number ID from Meta | For WhatsApp |
| `WHATSAPP_PHONE_NUMBER` | Recipient phone number with country code (e.g. "+33123456789") | For WhatsApp |
| `WHATSAPP_GROUP_NUMBERS` | Comma-separated phone numbers for group messaging | For WhatsApp groups |

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

## Delivery Methods

### Email via Gmail

The script sends emails via Gmail SMTP using an [App Password](https://myaccount.google.com/apppasswords). You need 2-Step Verification enabled on your Google account.

### WhatsApp via Meta Business API

The script can also send reports via WhatsApp using Meta's WhatsApp Business API. This is completely headless and works in automated environments like GitHub Actions.

#### Setting up WhatsApp Business API

1. **Create a Meta Business Account**
   - Go to [Meta Business](https://business.facebook.com/)
   - Create a business account if you don't have one

2. **Set up WhatsApp Business API**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Create a new app and select "Business" as the app type
   - Add WhatsApp product to your app
   - Follow the setup wizard to get your phone number verified

3. **Get your credentials**
   - **Access Token**: From your app dashboard → WhatsApp → API Setup
   - **Phone Number ID**: From your app dashboard → WhatsApp → API Setup
   - **Recipient Number**: The phone number to send messages to (with country code)

4. **Test your setup**
   ```bash
   # Add your WhatsApp credentials to .env
   META_ACCESS_TOKEN=your_access_token_here
   META_PHONE_NUMBER_ID=your_phone_number_id_here
   WHATSAPP_PHONE_NUMBER=+33123456789
   
   # Test locally
   python main.py
   ```

5. **Troubleshooting**
   - **Recipient phone number not in allowed list** → Add the recipient number to the 'To' list in your API Setup from your App at https://developers.facebook.com/

#### WhatsApp Features

- **Individual messaging**: Send to a single phone number
- **Group messaging**: Send to multiple phone numbers (simulated groups)
- **Clean formatting**: Long separator lines are automatically removed for better mobile readability
- **Emoji support**: Reports include emojis for better visual appeal

#### WhatsApp Rate Limits

⚠️ **Important**: WhatsApp Business API has a rate limit of **1 message per 24 hours** per recipient for automated messages.

- **Reset timer**: To reset the 24-hour limit, the recipient must reply to the bot on WhatsApp thread
- **Manual trigger**: If you need to send reports more frequently, reply to any previous bot message first
- **Scheduling**: The weekly automation respects this limit by sending only on Fridays

#### WhatsApp vs Email

| Feature | Email | WhatsApp |
|---------|--------|----------|
| Rich formatting | HTML + Text | Text only |
| Attachments | Yes | No |
| Delivery speed | Fast | Instant |
| Mobile-friendly | Good | Excellent |
| Setup complexity | Simple | Moderate |
| Cost | Free | API usage fees apply |
