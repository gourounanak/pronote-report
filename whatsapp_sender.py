"""
Sends the report to WhatsApp using Meta Graph API.
This module handles WhatsApp message sending completely headless without browser interaction.
"""

import os
import json
import requests
from typing import Optional

from report import build_whatsapp_report


def _clean_whatsapp_text(text: str) -> str:
    """
    Clean up text formatting for WhatsApp by removing long separator lines.
    
    Args:
        text: The raw text to clean
        
    Returns:
        Cleaned text with long dash and equals lines removed
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip lines that are mostly dashes (─) or equals (=) signs
        stripped = line.strip()
        if len(stripped) > 10:  # Only check lines longer than 10 characters
            # Count dashes and equals signs
            dash_count = stripped.count('─') + stripped.count('-')
            equals_count = stripped.count('=')
            total_chars = len(stripped)
            
            # If more than 80% of the line is dashes or equals, skip it
            if (dash_count + equals_count) / total_chars > 0.8:
                continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def send_whatsapp_report(
    subject: str,
    text_body: str,
    phone_number: Optional[str] = None,
    grades_by_child: Optional[dict] = None,
    days: int = 14
) -> None:
    """
    Send the report via WhatsApp using Meta Graph API (completely headless).
    
    Args:
        subject: The subject/title of the report
        text_body: The plain text body of the report (fallback if grades_by_child not provided)
        phone_number: The phone number to send to (with country code, e.g. "+33123456789")
        grades_by_child: Dictionary of grades data for WhatsApp-specific formatting
        days: Number of days to include in the report
    
    Required env vars:
        META_ACCESS_TOKEN — Your Meta WhatsApp Business API access token
        META_PHONE_NUMBER_ID — Your Meta WhatsApp Business phone number ID
        WHATSAPP_PHONE_NUMBER — recipient phone number with country code (e.g. "+33123456789")
    
    Note:
        - Completely headless, no browser interaction required
        - Works in GitHub Actions and any automated environment
        - Requires Meta WhatsApp Business API setup
        - Uses WhatsApp-specific formatting with emoji and bold names when grades_by_child is provided
    """
    if not phone_number:
        phone_number = os.environ["WHATSAPP_PHONE_NUMBER"]
    
    # Get Meta Graph API credentials
    access_token = os.environ["META_ACCESS_TOKEN"]
    phone_number_id = os.environ["META_PHONE_NUMBER_ID"]
    
    # Remove + prefix from phone number if present (Meta API expects numbers without +)
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    
    # Use WhatsApp-specific formatting if grades data is provided, otherwise use fallback text
    if grades_by_child is not None:
        whatsapp_body = build_whatsapp_report(grades_by_child, days=days)
        cleaned_text_body = _clean_whatsapp_text(whatsapp_body)
        # The WhatsApp report already includes the emoji and title, so we don't need to add it again
        full_message = cleaned_text_body
    else:
        # Fallback to original text body formatting
        cleaned_text_body = _clean_whatsapp_text(text_body)
        full_message = f"📊 {subject}\n\n{cleaned_text_body}"
    
    # Meta Graph API endpoint
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    # Request headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": full_message
        }
    }
    
    print(f"Sending WhatsApp message to +{phone_number}")
    
    try:
        # Send WhatsApp message via Meta Graph API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        message_id = result.get("messages", [{}])[0].get("id", "unknown")
        
        print(f"WhatsApp message sent successfully to +{phone_number}")
        print(f"Message ID: {message_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not send WhatsApp message — {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                print(f"API Error Details: {json.dumps(error_details, indent=2)}")
            except:
                print(f"Raw Error Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"ERROR: Could not send WhatsApp message — {e}")
        raise


def send_whatsapp_instant(
    subject: str,
    text_body: str,
    phone_number: Optional[str] = None,
    grades_by_child: Optional[dict] = None,
    days: int = 14
) -> None:
    """
    Send WhatsApp message instantly using Meta Graph API.
    
    Args:
        subject: The subject/title of the report
        text_body: The plain text body of the report (fallback if grades_by_child not provided)
        phone_number: The phone number to send to (with country code)
        grades_by_child: Dictionary of grades data for WhatsApp-specific formatting
        days: Number of days to include in the report
    
    Note:
        With Meta Graph API, all messages are sent instantly, so this is the same as send_whatsapp_report.
    """
    send_whatsapp_report(subject, text_body, phone_number, grades_by_child, days)


def send_whatsapp_group(
    subject: str,
    text_body: str,
    group_id: Optional[str] = None,
    grades_by_child: Optional[dict] = None,
    days: int = 14
) -> None:
    """
    Send the report to multiple WhatsApp numbers (simulating group functionality).
    
    Args:
        subject: The subject/title of the report
        text_body: The plain text body of the report (fallback if grades_by_child not provided)
        group_id: Comma-separated list of phone numbers (e.g. "+33123456789,+33987654321")
        grades_by_child: Dictionary of grades data for WhatsApp-specific formatting
        days: Number of days to include in the report
    
    Required env vars:
        WHATSAPP_GROUP_NUMBERS — Comma-separated phone numbers with country codes
    
    Note:
        Meta Graph API doesn't support WhatsApp groups directly, so this sends to multiple individual numbers.
    """
    if not group_id:
        group_id = os.environ.get("WHATSAPP_GROUP_NUMBERS")
    
    if not group_id:
        raise ValueError("WHATSAPP_GROUP_NUMBERS environment variable is required for group messaging")
    
    # Parse comma-separated phone numbers
    phone_numbers = [num.strip() for num in group_id.split(",")]
    
    print(f"Sending WhatsApp message to {len(phone_numbers)} recipients")
    
    # Send to each number individually
    success_count = 0
    for phone_number in phone_numbers:
        try:
            send_whatsapp_report(subject, text_body, phone_number, grades_by_child, days)
            success_count += 1
        except Exception as e:
            print(f"ERROR: Failed to send to {phone_number} — {e}")
            # Continue sending to other numbers even if one fails
            continue
    
    print(f"WhatsApp group messages sent successfully to {success_count}/{len(phone_numbers)} recipients")