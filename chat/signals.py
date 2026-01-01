from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwarg):
    if created:
        receiver_user = instance.room.members.exclude(
            id=instance.sender.id)
        receiver_user = instance.room.members.exclude(id=instance.sender.id)
        save_notification(instance=instance, recipient=receiver_user)


def save_notification(instance, recipient):
    notification = [Notification(
        message=instance,
        recipient=user
    ) for user in recipient]
    Notification.objects.bulk_create(notification)
    channel_layer = get_channel_layer()
    for user in recipient:
        # print(x.id)
        # TODO :instead of direct sending fetch from db and send notification, only send unseen message to the group or user and
        group_name = f"notify_{user.id}"
        notification_context = [{
            "message": f"New message from {instance.sender.first_name}",
            "sender_username": instance.sender.username,
            "is_group": instance.room.is_group,
            "group_name": instance.room.room_name,
            "is_read": False,
        }]
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "notification_context": notification_context,
            }
        )
