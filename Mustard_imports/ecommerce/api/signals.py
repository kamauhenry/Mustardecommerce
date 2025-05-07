from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from ecommerce.models import Order
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=User, dispatch_uid='send_welcome_email')
def send_welcome_email(sender, instance, created, **kwargs):
    logger.info('Sending welcome email...')
    if created:
        try:
            send_mail(
                'Welcome',
                'Thank you for signing up!',
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False,
            )
            logger.info(f"Welcome email sent to {instance.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {instance.email}: {str(e)}", exc_info=True)

@receiver(post_save, sender=Order, dispatch_uid='send_shipped_email')
def send_shipped_email(sender, instance, created, raw, **kwargs):
    if raw:  # Skip if loading fixtures
        return
    if not created:  # Only handle updates, not new orders
        try:
            # Get the previous state of the order
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.delivery_status != 'shipped' and instance.delivery_status == 'shipped' and instance.user.email:
                logger.info(f"Sending shipped email for order {instance.order_number} to {instance.user.email}")
                try:
                    html_message = render_to_string('emails/shipped_email.html', {
                        'user_name': instance.user.get_full_name() or instance.user.username,
                        'order_number': instance.order_number,
                        'delivery_location': instance.delivery_location.address if instance.delivery_location else 'N/A',
                        'site_url': settings.SITE_URL,
                        'year': 2025,
                    })
                    logger.info("Successfully rendered shipped_email.html")
                except Exception as e:
                    logger.error(f"Failed to render template emails/shipped_email.html: {str(e)}", exc_info=True)
                    return
                send_mail(
                    subject=f"Your Order #{instance.order_number} Has Arrived",
                    message="Your order has arrived and is ready for pickup.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(f"Shipped email sent for order {instance.order_number} to {instance.user.email}")
        except Order.DoesNotExist:
            logger.error(f"Order {instance.pk} not found during shipped email signal", exc_info=True)
        except Exception as e:
            logger.error(f"Failed to send shipped email for order {instance.order_number}: {str(e)}", exc_info=True)