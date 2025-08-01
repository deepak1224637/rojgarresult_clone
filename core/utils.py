from django.core.mail import send_mail
from django.conf import settings

def send_notification(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False
    )
