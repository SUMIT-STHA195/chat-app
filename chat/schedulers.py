from django_q.tasks import schedule
from django_q.models import Schedule

schedule(
        'chat.tasks.send_unseen_notification',
        name=f'Unseen Notification Reminder',
        schedule_type=Schedule.MINUTES,
        minutes=1,
        repeats=-1
    )


