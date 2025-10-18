import requests
from datetime import datetime
from flask import current_app


def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def compute_total(items, shipping=0.0):
    subtotal = sum(i['unit_price'] * i['quantity'] for i in items)
    tax = subtotal * 0.05  # 5% tax
    total = subtotal + tax + shipping
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "shipping": round(shipping, 2),
        "total": round(total, 2)
    }


def reserve_inventory(items):
    """Mock Inventory reservation"""
    for item in items:
        if item["quantity"] > 100:
            return False
    return True


class PaymentService:
    @staticmethod
    def add_payment(order_id, amount, method="CARD"):
        """Calls the Payment Service /v1/payments/charge"""
        url = f"{current_app.config['PAYMENT_SERVICE_URL']}/v1/payments/charge"
        payload = {
            "order_id": order_id,
            "amount": amount,
            "method": method
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            return resp.status_code, resp.json()
        except Exception as e:
            return 500, {"status": "FAILED", "error": str(e)}

    @staticmethod
    def refund_payment(order_id):
        """Refund a payment"""
        url = f"{current_app.config['PAYMENT_SERVICE_URL']}/v1/payments/{order_id}/refund"
        try:
            resp = requests.get(url, timeout=5)
            return resp.status_code, resp.json()
        except Exception as e:
            return 500, {"status": "FAILED", "error": str(e)}
