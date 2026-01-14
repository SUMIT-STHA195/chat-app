# celeryconfig.py
from celery.schedules import crontab

broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'Asia/Kathmandu'
enable_utc = False
worker_concurrency = 2

# CRITICAL FIX
worker_prefetch_multiplier = 1
task_acks_late = True

# Optional but recommended
task_track_started = True
task_ignore_result = True
task_reject_on_worker_lost = True

# Ensure the task path matches exactly how Celery sees it
beat_schedule = {
    'send-every-minute': {
        'task': 'chat.tasks.send_unseen_notification',
        'schedule': crontab(minute='*/1'),
    }
}
