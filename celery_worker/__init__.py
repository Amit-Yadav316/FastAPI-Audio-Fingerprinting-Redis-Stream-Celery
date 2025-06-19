from celery import Celery

from app.config.config import settings  

celery_app = Celery(
    "worker",
    broker=settings.redis_celery_broker_url,
    backend=settings.redis_celery_backend_url,
)

celery_app.autodiscover_tasks(["celery_worker"])