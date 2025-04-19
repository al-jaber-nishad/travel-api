from celery import shared_task
from django.core.cache import cache
import json
from travel.utils import calculate_top_districts

@shared_task(name='core.tasks.refresh_top_districts')
def refresh_top_districts():
    print("Refreshing top districts via Celery...")
    data = calculate_top_districts()
    cache.set("top_districts", json.dumps(data), timeout=3600)
    print("Top districts cached.")