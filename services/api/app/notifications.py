"""Delivery is injected; local runs do not transmit customer details."""

from sqlalchemy import select
from .models import Outbox


def process_outbox(db, deliver):
    for event in db.scalars(
        select(Outbox).where(Outbox.status != "delivered").limit(100)
    ):
        event.attempts += 1
        try:
            deliver(event.lead_id)
            event.status = "delivered"
            event.last_error = ""
        except Exception:
            event.status = "failed"
            event.last_error = "Notification delivery failed; retry required"
        db.commit()
