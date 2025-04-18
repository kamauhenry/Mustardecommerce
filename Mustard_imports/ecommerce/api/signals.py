from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

@receiver(post_save, sender=User, dispatch_uid='send_welcome_email')
def send_welcome_email(sender, instance, created, **kwargs):
    print('signal fired...')
    if created:
        send_mail(
            'Welcome',
            'Thank you for signing up!',
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )