from celery import Celery, Task

# Move FlaskTask to module level for pickling support
class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        # app will be set as attribute on the task instance
        with self.app.app_context():
            return self.run(*args, **kwargs)

def celery_init_app(app):
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object('backend.celery_config')
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    # Attach Flask app to Celery tasks for context
    celery_app.Task.app = app
    return celery_app 