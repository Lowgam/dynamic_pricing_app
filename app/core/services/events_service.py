# Module : events_service.py
# Purpose : module to call the query to verify if there are events opened from 7 or more days

from app.database.queries import has_stale_change_price_events

def has_events_to_sync(days: int = 7) -> bool:
    return has_stale_change_price_events(days)