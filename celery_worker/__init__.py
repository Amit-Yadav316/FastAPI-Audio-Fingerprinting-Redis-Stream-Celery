from celery import Celery
import os
import sys

from app.config.config import settings  
sys.path.append(os.path.dirname(__file__))

celery_app = Celery(
    "worker",
    broker=settings.redis_celery_broker_url,
    backend=settings.redis_celery_backend_url,
)
from tasks.fingerprinting import generate_fingerprint_task
from tasks.matching import match_fingerprint_task

celery_app.autodiscover_tasks(["tasks"])
print("Discovered tasks:", celery_app.tasks.keys())