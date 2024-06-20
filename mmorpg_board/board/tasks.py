# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser

@shared_task
def send_verification_email_task(user_id, code):
    try:
        user = CustomUser.objects.get(id=user_id)
        subject = 'Email Verification'
        message = f'Your verification code is {code}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, email_from, recipient_list)
    except CustomUser.DoesNotExist:
        pass  # Обработка ошибки, если пользователь не найден
