# Import .env
from dotenv import load_dotenv
load_dotenv()
# Error
from slack_sdk.errors import SlackApiError
# Rest of the packages
import os
import logging
from slack_sdk import WebClient


#========================================================================================#


# Import credentials from a .env
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL")

# Initialize the WEbClient with bot token
client = WebClient(token=SLACK_TOKEN)

def send_slack_notification(message_text):
    try:
        # Call the chat.postMessage API Method
        response = client.chat_postMessage(
            channel=CHANNEL_ID,
            text=message_text,
        )
        print(f"✅ Notification sent successfully! Timestamp: {response['ts']}")

    except SlackApiError as e:
        # Handle server-side errors retued by the API
        logging.error(f"Slack API error occured: {e}")

    except Exception as e:
        # Handle connection errors or other runtime failures
        logging.error(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensre token is set before rnning
    if not SLACK_TOKEN:
        raise ValueError("SLACK_BOT_TOKEN environ,ent variable is missing")

    send_slack_notification("🚀 Hello from Python! Your automated notification script is operational.")
