from random import choice

from api.models import ActivityLog
from django.contrib.auth.models import User
from django.db import models
from twilio.rest import Client


class TwoFactorAuthCode(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=6)
    sent_on = models.DateTimeField(auto_now_add=True)

    @classmethod
    def send_code(cls, user, to_phone):
        account_sid = 'AC1b30d7a8f3d4240fb58560e3f21ebe45'
        auth_token = 'f57eaede6e648dd57209e561f5fd2172'
        client = Client(account_sid, auth_token)
        digits = '0123456789'
        code = ''.join([choice(digits) for i in range(6)])
        cls.objects.create(
            user=user,
            code=code,
        )
        message = client.messages.create(
            to=to_phone,  # '+16473790277'
            from_='+12057363740',
            body='Your auth code: ' + code,
        )

    @classmethod
    def validate_code(cls, user, code):
        if user.is_anonymous:
            return False
        existing = cls.objects.filter(
            user=user, code=code
        ).order_by('-sent_on').first()
        if existing is None:
            ActivityLog.objects.create(
                user=user,
                action='User entered incorrect two-factor auth code'
            )
            return False
        existing.delete()
        ActivityLog.objects.create(
            user=user,
            action='User entered correct two-factor auth code'
        )
        return True
