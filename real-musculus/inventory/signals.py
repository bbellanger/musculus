from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from notifications.slack import send_slack_notification

@receiver(post_save, sender=Order)
def notify_slack_on_order_created(sender, instance, created, **kwargs):
    if not created:
        return # So that it only fire on INSERT, not every save/update

    send_slack_notification(
        f"🛒 New order #{instance.id} | {instance.name} - requested by {instance.requested_by}"
)
