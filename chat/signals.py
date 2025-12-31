from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification
from asgiref.sync import sync_to_async


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwarg):
    if created:
        if instance.room.is_group:
            receiver_user=instance.room.members.exclude(id=instance.sender.id)
            save_notification(instance=instance,recipient=receiver_user)
        else:
            receiver_user = instance.room.members.exclude(
                id=instance.sender.id)
            receiver_user=instance.room.members.exclude(id=instance.sender.id)
            save_notification(instance=instance,recipient=receiver_user)

def save_notification(instance,recipient):
    notification=[Notification(
                message=instance,
                recipient=user
            ) for user in recipient]
    Notification.objects.bulk_create(notification)
