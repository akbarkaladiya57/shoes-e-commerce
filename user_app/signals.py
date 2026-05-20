from django.db.models.signals import post_save
from django.dispatch import receiver

from snakesole.utils import send_email
from user_app.models import OtpVerification
from django.conf import settings



@receiver(post_save, sender=OtpVerification)
def send_otp_email(sender, instance, created, **kwargs):
    if created:
        html_content = f"""
        <h2>Your OTP Code</h2>
        <p>Your OTP is:</p>
        <h1>{instance.otp}</h1>
        """

        send_email(
            to_email=instance.user.email,
            subject="Your OTP Code",
            html_content=html_content
        )
