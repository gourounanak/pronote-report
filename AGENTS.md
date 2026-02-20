# AGENTS.md - Repository Navigation Guide

## Project Overview
This is a **Pronote Weekly Report** automation tool that:
- Fetches grades from Pronote for all children of a parent account
- Generates formatted reports (text + HTML)
- Sends weekly reports every Friday via Gmail SMTP and/or WhatsApp
- Supports WhatsApp messaging via Meta Business API (completely headless)
- Runs automatically via GitHub Actions

## Repository Structure

```
├── main.py                 # Entry point - orchestrates the entire flow
├── fetcher.py             # Pronote API integration - fetches grades data
├── mailer.py              # Email sending via Gmail SMTP
├── whatsapp_sender.py     # WhatsApp messaging via Meta Business API
├── report.py              # Report formatting (text and HTML)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # User documentation
└── .github/workflows/
    └── weekly_report.yml  # GitHub Actions automation
```

## Key Components

### Core Files
- **`main.py`**: Main orchestrator that loads environment, fetches grades, builds reports, and sends via email/WhatsApp
- **`fetcher.py`**: Contains `GradeEntry` dataclass and `fetch_grades()` function using pronotepy library
- **`mailer.py`**: Handles Gmail SMTP email sending with `send_report()` function
- **`whatsapp_sender.py`**: Handles WhatsApp messaging via Meta Business API with text cleaning for mobile
- **`report.py`**: Formats data into text and HTML reports with French date formatting

### Configuration
- **`.env.example`**: Template for local development environment variables
- **Environment Variables Required**:
  - `PRONOTE_URL`: School's Pronote parent page URL
  - `PRONOTE_USERNAME` & `PRONOTE_PASSWORD`: Pronote credentials
  - `GMAIL_ADDRESS` & `GMAIL_APP_PASSWORD`: Gmail SMTP credentials (optional)
  - `EMAIL_TO`: Recipient email address(es) (optional)
  - `META_ACCESS_TOKEN` & `META_PHONE_NUMBER_ID`: Meta WhatsApp Business API credentials (optional)
  - `WHATSAPP_PHONE_NUMBER`: Recipient WhatsApp number with country code (optional)

### Automation
- **`.github/workflows/weekly_report.yml`**: Runs every Friday at 7 AM Paris time
- Uses GitHub repository secrets for sensitive configuration

## Development Guidelines

### Local Testing
1. Copy `.env.example` to `.env` and fill in actual values
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

### Security Best Practices
- **NEVER commit `.env` file** (already in .gitignore)
- Use GitHub repository secrets for production deployment
- Gmail requires App Password, not regular password
- All sensitive data should be in environment variables

### Code Architecture
- **Separation of Concerns**: Each file has a single responsibility
- **Type Hints**: Modern Python with proper typing
- **Error Handling**: Graceful failure with meaningful error messages
- **Dataclass Usage**: Clean data structures with `GradeEntry`

### Key Functions to Know
- `fetch_grades()`: Returns `dict[str, list[GradeEntry]]` mapping child names to their grades
- `build_text_report()` & `build_html_report()`: Format grades into email bodies
- `send_report()`: Sends multipart email with both text and HTML versions
- `send_whatsapp_report()`: Sends WhatsApp message via Meta Business API with cleaned formatting
- `send_whatsapp_group()`: Sends WhatsApp messages to multiple recipients
- `_clean_whatsapp_text()`: Removes long separator lines for better mobile readability

## Potential Enhancement Areas
- Add more email providers beyond Gmail
- Implement grade comparison/trends over time
- Add configuration for different report frequencies
- Implement notification webhooks (Slack, Discord, etc.)
- Add grade filtering/alerting for specific conditions

## Dependencies
- **pronotepy**: Core library for Pronote API interaction (v2.0+)
- **python-dotenv**: Environment variable management (v1.0.0+)
- **Standard Library**: smtplib, email, datetime, dataclasses

## Deployment Notes
- Requires Python 3.12+ (3.9 with LibreSSL has known decryption issues)
- GitHub Actions runs on ubuntu-latest with 10-minute timeout
- Cron schedule uses UTC time, adjusted for Paris timezone
- Manual workflow dispatch available for testing

## Troubleshooting Tips
- Check Pronote URL format (must end with `parent.html`)
- Verify Gmail App Password (16 characters, not regular password)
- Ensure 2-Step Verification is enabled on Google account
- Test locally before deploying to GitHub Actions
- Check GitHub Actions logs for deployment issues