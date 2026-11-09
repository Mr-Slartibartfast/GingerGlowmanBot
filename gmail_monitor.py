
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json") # save credentials json in folder for project
TOKEN_FILE = os.path.join(BASE_DIR, "token.json") # save the token json in folder for project




def diagnostic_search(service):

    query = (
    'newer_than:90d '
    '{subject:"back in stock" '
    'subject:"available again" '
    'subject:"restocked"}'
    )

    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=20
    ).execute()

    messages = results.get("messages", [])

    print(f"\nFound {len(messages)} matching emails\n")

    for message in messages:

        details = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = details.get("payload", {}).get(
            "headers", []
        )

        for header in headers:
            if header["name"] in ["From", "Subject", "Date"]:
                print(f'{header["name"]}: {header["value"]}')

        print("-" * 50)



def authenticate_gmail():
    """Authenticate with Gmail using OAuth."""

    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json not found!"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def check_target_emails(service):
    """Find recent emails from Target."""

    results = service.users().messages().list(
        userId="me",
        q='newer_than:90d {from:target.com from:targetemail.com "Target"}',
        maxResults=10
    ).execute()

    messages = results.get("messages", [])

    print(f"\nFound {len(messages)} Target email(s).\n")

    for message in messages:

        details = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = details.get("payload", {}).get(
            "headers", []
        )

        email_data = {
            header["name"]: header["value"]
            for header in headers
        }

        print("----------------------------------")
        print("From:", email_data.get("From", "Unknown"))
        print("Subject:", email_data.get("Subject", "No subject"))
        print("Date:", email_data.get("Date", "Unknown"))


def main():

    try:
        print("Connecting to Gmail...")

        service = authenticate_gmail()

        print("Gmail connection successful!")

        # check_target_emails(service)
        diagnostic_search(service)

    except HttpError as error:
        print(f"Gmail API error: {error}")

    except Exception as error:
        print(f"Application error: {error}")


if __name__ == "__main__":
    main()
