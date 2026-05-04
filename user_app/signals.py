from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from user_app.models import OtpVerification
from django.conf import settings



@receiver(post_save, sender=OtpVerification)
def send_otp_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP is {instance.otp}",
            from_email="your_email@gmail.com",
            recipient_list=[instance.user.email],
        )
