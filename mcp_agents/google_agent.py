import os
import base64
from email.message import EmailMessage
from datetime import datetime, timedelta
from langchain.tools import tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.modify'
]

def get_google_services():
    """Authenticates and returns Google Calendar and Gmail service clients."""
    creds = None
    token_path = 'token.json'
    creds_path = 'credentials.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    "credentials.json file nahi mili! Google Cloud Console se download karke project root mein rakhein."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    calendar_service = build('calendar', 'v3', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    return calendar_service, gmail_service

@tool
def google_calendar_tool(action: str, summary: str = "", start_time_iso: str = "", duration_hours: int = 1) -> str:
    """Useful to read or schedule meetings on Google Calendar.
    Parameters:
    - action: 'list' (to read upcoming meetings) or 'create' (to schedule a meeting).
    - summary: Title of the meeting.
    - start_time_iso: Start time in ISO format (e.g. '2026-10-05T15:00:00'). Default is tomorrow at 3 PM if empty.
    - duration_hours: Duration of meeting in hours (default 1).
    """
    try:
        cal_service, _ = get_google_services()
        
        if action.lower() == "list":
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = cal_service.events().list(
                calendarId='primary', timeMin=now,
                maxResults=5, singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            if not events:
                return "Google Calendar par koi aane wali meeting nahi mili."
            
            event_strings = [
                f"- {e.get('summary', 'No Title')} (Start: {e['start'].get('dateTime', e['start'].get('date'))})"
                for e in events
            ]
            return "Upcoming Meetings:\n" + "\n".join(event_strings)
            
        elif action.lower() == "create":
            if not start_time_iso:
                start_dt = datetime.now() + timedelta(days=1)
                start_dt = start_dt.replace(hour=15, minute=0, second=0, microsecond=0)
            else:
                start_dt = datetime.fromisoformat(start_time_iso)
                
            end_dt = start_dt + timedelta(hours=duration_hours)
            
            event = {
                'summary': summary or 'Team Meeting',
                'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Karachi'},
                'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Karachi'},
            }
            
            created_event = cal_service.events().insert(calendarId='primary', body=event).execute()
            return f"Meeting successfully scheduled on Google Calendar: '{created_event.get('summary')}' at {start_dt.strftime('%Y-%m-%d %H:%M')}. Link: {created_event.get('htmlLink')}"
            
        return f"Unknown calendar action: {action}"
    except Exception as e:
        return f"Google Calendar API Error: {str(e)}"

@tool
def google_gmail_tool(action: str, recipient: str, subject: str, body: str) -> str:
    """Useful to send emails or create email drafts via Gmail.
    Parameters:
    - action: 'send' or 'draft'
    - recipient: Target email address (e.g. 'ali@example.com')
    - subject: Subject line of the email
    - body: Content/body of the email
    """
    try:
        _, gmail_service = get_google_services()
        
        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        if action.lower() == "draft":
            draft = gmail_service.users().drafts().create(
                userId="me",
                body={'message': create_message}
            ).execute()
            return f"Draft email successfully created in Gmail! Draft ID: {draft['id']} (To: {recipient}, Subject: '{subject}')"
            
        elif action.lower() == "send":
            sent_msg = gmail_service.users().messages().send(
                userId="me",
                body=create_message
            ).execute()
            return f"Email successfully sent via Gmail! Message ID: {sent_msg['id']} (To: {recipient}, Subject: '{subject}')"
            
        return f"Unknown Gmail action: {action}"
    except Exception as e:
        return f"Gmail API Error: {str(e)}"