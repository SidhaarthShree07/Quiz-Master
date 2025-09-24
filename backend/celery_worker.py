import os
import sys
from celery import Celery

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Create Celery app
celery = Celery('quiz_master', include=['tasks'])


# Import beat schedule and timezone from celery_beat_schedule.py
try:
    from celery_beat_schedule import beat_schedule, timezone as beat_timezone
    celery.conf.update(
        broker_url="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/1",
        beat_schedule=beat_schedule,
        timezone=beat_timezone,
        broker_connection_retry_on_startup=True,
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        enable_utc=True
    )
    print('[Celery Worker] Beat schedule loaded from celery_beat_schedule.py')
except ImportError as e:
    print('[Celery Worker] ERROR importing beat schedule:', e)

# Import tasks to register them
try:
    import tasks
    print('[Celery Worker] tasks module imported, tasks should be registered.')
    print(f'[Celery Worker] Registered tasks: {list(celery.tasks.keys())}')
    
    # Verify the specific task is registered
    if 'send_daily_gchat_reminders' in celery.tasks:
        print('[Celery Worker] ✅ send_daily_gchat_reminders task is registered')
    else:
        print('[Celery Worker] ❌ send_daily_gchat_reminders task is NOT registered')
        
except ImportError as e:
    print('[Celery Worker] ERROR importing tasks:', e)