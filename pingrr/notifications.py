import logging

from pushover import Pushover
from slack import Slack

logger = logging.getLogger("Notifications")

SERVICES = {
    'pushover': Pushover,
    'slack': Slack
}


class Notifications:
    def __init__(self):
        self.services = []
        logger.debug("Initialized")

    def load(self, **kwargs):
        if 'service' not in kwargs:
            logger.error("You must specify a service to load with the service parameter")
            return False
        elif kwargs['service'].lower() not in SERVICES:
            logger.error("You specified an invalid service to load: %s", kwargs['service'])
            return False

        try:
            chosen_service = SERVICES[kwargs['service']]
            del kwargs['service']

            # load service
            service = chosen_service(**kwargs)
            self.services.append(service)

        except Exception:
            logger.exception("Exception while loading service, kwargs=%r:", kwargs)

    def send(self, **kwargs):
        # remove service keyword if supplied
        if 'service' in kwargs:
            # send notification to specified service
            chosen_service = kwargs['service'].lower()
            del kwargs['service']
        else:
            chosen_service = None

        # send notification(s)
        for service in self.services:
            if chosen_service and service.NAME.lower() != chosen_service:
                continue
            elif service.send(**kwargs):
                logger.info("Sent notification with %s", service.NAME)
