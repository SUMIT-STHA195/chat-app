from celery import Celery
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_app.settings')

# The first argument is the name of the current module
app = Celery('chat_app')

# Load configuration from the celeryconfig module
# Make sure 'celeryconfig' is in your Python path
app.config_from_object('celeryconfig')

# Optional: automatically discover tasks in your project
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
