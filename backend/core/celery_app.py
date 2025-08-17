"""
Celery configuration for async tasks
"""
from celery import Celery
import os

def create_celery_app(app=None):
    """Create Celery app"""
    celery = Celery(
        'aruco_generator',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    )
    
    # Configure Celery
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        result_expires=3600,
        task_track_started=True,
        task_time_limit=300,  # 5 minutes
        task_soft_time_limit=240,  # 4 minutes
        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,
    )
    
    if app:
        celery.conf.update(app.config)
        
        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context"""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery

# Create celery instance
celery_app = create_celery_app()