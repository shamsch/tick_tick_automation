import os
import requests
from datetime import datetime, timezone
import pytz
import boto3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from icalendar import Calendar

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# DynamoDB Table Name
DYNAMO_TABLE_NAME = os.getenv("DYNAMO_TABLE_NAME", "CalendarEvents")

# Gmail credentials
GMAIL_USER = os.getenv("GMAIL_USER", "your_email@gmail.com")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "your_password")

# Calendar links
CALENDAR_LINKS = [
    os.getenv("CALENDAR_LINK_1", "https://example.com/calendar1.ics"),
    os.getenv("CALENDAR_LINK_2", "https://example.com/calendar2.ics"),
]

# Email address to send notifications
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "your_email@domain.com")

def fetch_calendar_events(calendar_links):
    """Fetch events from calendar links"""
    events = []
    for link in calendar_links:
        try:
            response = requests.get(link)
            response.raise_for_status()
            calendar = Calendar.from_ical(response.text)
            events.extend(parse_ics_events(calendar))
        except Exception as e:
            print(f"Failed to fetch calendar from {link}: {e}")
    return events

def parse_ics_events(calendar):
    """Parse ICS calendar to extract events"""
    events = []
    now = datetime.now(pytz.utc)
    for component in calendar.walk():
        if component.name == "VEVENT":
            event_start = component.get("DTSTART").dt
            if isinstance(event_start, datetime):
                event_start = event_start.astimezone(timezone.utc)
            else:
                event_start = datetime.combine(event_start, datetime.min.time()).astimezone(timezone.utc)
            if event_start > datetime.now(timezone.utc):
                events.append({
                    'event_id': component.get("UID"),
                    'summary': component.get("SUMMARY"),
                    'description': component.get("DESCRIPTION", ''),
                    'start': event_start.isoformat()
                })
    return events

def get_all_sent_events():
    """Get all events sent via email"""
    table = dynamodb.Table(DYNAMO_TABLE_NAME)
    response = table.scan(ProjectionExpression="event_id")
    return {item['event_id'] for item in response.get('Items', [])}

def add_event_to_dynamodb(event):
    """Add event to DynamoDB"""
    table = dynamodb.Table(DYNAMO_TABLE_NAME)
    table.put_item(
        Item=event,
        ConditionExpression="attribute_not_exists(event_id)"
    )

def send_email_notification(email, events):
    """Send email notification with fetched events using Gmail SMTP"""
    if not events:
        return

    for event in events:
        event_start = datetime.fromisoformat(event['start'])
        event_start = event_start.astimezone(pytz.timezone("Europe/Helsinki"))
        formatted_start = event_start.strftime("%I:%M%p %B %d, %Y")
        subject = f"{event.get('summary')} {formatted_start}"
        body = f"{event.get('description', '')}\n#automation !High Priority"

        try:
            msg = MIMEMultipart()
            msg['From'] = GMAIL_USER
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, email, msg.as_string())
            server.quit()

            add_event_to_dynamodb(event)

            print(f"Email sent successfully for event {event['summary']}")

        except Exception as e:
            print(f"Failed to send email for event {event['summary']}: {e}")

def lambda_handler(event, context):
    """Lambda entry point"""

    # Fetch events
    print("Fetching calendar events...")
    events = fetch_calendar_events(CALENDAR_LINKS)

    print("Fetching sent event IDs from DynamoDB...")
    sent_event_ids = get_all_sent_events()

    new_events = [e for e in events if e['event_id'] not in sent_event_ids]
    print(f"New events to process: {len(new_events)}")

    send_email_notification(EMAIL_ADDRESS, new_events)

    print("Processing completed.")
    return {
        'statusCode': 200,
        'body': 'Calendar events processed successfully.'
    }
