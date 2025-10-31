from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation_email(to_email, booking_details):
    subject = 'Booking Confirmation'
    message = f"Dear customer,\n\nYour booking was successful!\n\nDetails:\n{booking_details}\n\nThank you for choosing us!"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
    return f"Email sent to {to_email}"
