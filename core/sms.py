import importlib
from hashlib import sha1

from django.conf import settings


class ConsoleSMSBackend:
    def send(self, sms):
        print("---")
        print(f"SMS sent from {sms.from_number} to {sms.to_number}:")
        print(sms.body)
        print("---")
        return "console-" + sha1().hexdigest()[:32]


class TwilioSMSBackend:
    def __init__(
        self,
        account_sid=settings.TWILIO_ACCOUNT_SID,
        auth_token=settings.TWILIO_AUTH_TOKEN,
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token

    def send(self, sms):
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        client = Client(self.account_sid, self.auth_token)
        try:
            message = client.messages.create(
                body=sms.body, from_=sms.from_number, to=sms.to_number
            )
        except TwilioRestException as e:
            raise e
        else:
            return message.sid


class SMS:
    from_number = "bouldertime"

    def get_backend(self):
        return getattr(importlib.import_module("core.sms"), settings.SMS_BACKEND)()

    def __init__(self, to_number, body):
        self.to_number = to_number
        self.body = body

    def send(self):
        return self.get_backend().send(self)
