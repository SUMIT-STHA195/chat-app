from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery import shared_task
from django.contrib.auth import get_user_model


@shared_task
def send_unseen_notification():
    # Get user who have unread notification
    User = get_user_model()
    users_with_unread = User.objects.filter(
        notification__is_read=False).distinct()
    channel_layer = get_channel_layer()
    for user in users_with_unread:
        count = Notification.objects.filter(
            recipient=user, is_read=False).count()
        group_name = f"notify_{user.id}"

        print(
            f"Actually sending to {user.username} (ID: {user.id}) with count: {count}")

        reminder_context = {
            'message': f'You have {count} unseen messages'
        }

        # This MUST be inside the loop to notify every user
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "resend_notification",
                "reminder_context": reminder_context,
            }
        )
