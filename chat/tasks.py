from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_unseen_notification():
    unseen_notification = Notification.objects.filter(is_read=False)
    channel_layer = get_channel_layer()
    if unseen_notification.exists():

        print("Notifying User")
        count = 0
        group_name = ""
        for notification in unseen_notification:
            print(f"sending to ------------{notification.recipient.username}")
            group_name = f"notify_{notification.recipient.id}"
            print(f'---------{group_name}')
            count += 1
        print(count)
        reminder_context = {
            'message': f'You have {count} unseen messages'
        }
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "resend_notification",
                "reminder_context": reminder_context,
            }
        )
