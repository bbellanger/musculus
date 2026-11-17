import logging
from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

def send_slack_notification(message_text):
    token = settings.SLACK_BOT_TOKEN
    channel = settings.SLACK_CHANNEL

    if not token or not channel:
        logger.warning("Slack not configured; skipping notifications.")
        return

    client = WebClient(token=token) # created per-call, not at import time

    try:
        response = client.chat_postMessage(channel=channel, text=message_text)
        logger.info(f"Slack notification sent. th={response['ts']}")
    except SlackApiError as e :
        logger.error("Slack API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending Slack notification: {e}")

