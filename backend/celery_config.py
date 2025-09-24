broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/1"
timezone = "Asia/Kolkata"
broker_connection_retry_on_startup = True
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True 