import logging
import requests

logger = logging.getLogger(__name__)


class Slack:
    NAME = "Slack"

    def __init__(self, webhook_url, sender_name='Notifications', sender_icon=':exclamation:', channel=None):
        self.webhook_url = webhook_url
        self.sender_name = sender_name
        self.sender_icon = sender_icon
        self.channel = channel
        logger.debug("Initialized")

    def send(self, **kwargs):
        if not self.webhook_url or not self.sender_name or not self.sender_icon:
            logger.error("You must specify an webhook_url, sender_name and sender_icon when initializing this class")
            return False

        # send notification
        try:
            payload = {
                'text': kwargs['message'],
                'username': self.sender_name,
                'icon_emoji': self.sender_icon,
            }
            if self.channel:
                payload['channel'] = self.channel

            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            return True if resp.status_code == 200 else False

        except Exception as ex:
            logger.exception("Error sending notification to %r", self.webhook_url)
        return False
