import uuid
from datetime import datetime


def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def process_payment(order_id, amount, method="CARD"):
    """Simulate a successful payment"""
    payment = {
        "payment_id": str(uuid.uuid4()),
        "order_id": order_id,
        "amount": amount,
        "method": method,
        "status": "SUCCESS",
        "reference": str(uuid.uuid4()),
        "created_at": now_iso()
    }
    return payment
