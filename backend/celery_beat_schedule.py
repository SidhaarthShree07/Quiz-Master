# Celery Beat schedule configuration
from celery.schedules import crontab

beat_schedule = {
    'send-daily-gchat-reminders': {
        'task': 'send_daily_gchat_reminders',
        'schedule': crontab(hour=11, minute=7),  # Every minute for testing
        # For production, use: crontab(hour=9, minute=0) for daily at 9 AM
    },
    'send-monthly-user-report': {
        'task': 'send_monthly_user_report',
        'schedule': crontab(minute=6, hour=11, day_of_month=31),
    },
}

timezone = 'Asia/Kolkata'
