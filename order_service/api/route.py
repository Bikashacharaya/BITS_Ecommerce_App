from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from api.actions import compute_total, reserve_inventory, now_iso, PaymentService

order_bp = Blueprint('orders', __name__)


@order_bp.route("/v1/orders", methods=["POST"])
def create_order():
    data = request.json
    mongo = current_app.mongo

    customer_id = data.get("customer_id")
    items = data.get("items", [])
    shipping = data.get("shipping", 0.0)

    if not customer_id or not items:
        return jsonify({"error": "customer_id and items are required"}), 400

    # Compute totals
    totals = compute_total(items, shipping)

    # Create base order
    order = {
        "customer_id": customer_id,
        "order_status": "PENDING",
        "payment_status": "UNPAID",
        "items": items,
        "totals": totals,
        "created_at": now_iso()
    }

    # Insert into MongoDB
    result = mongo.db.orders.insert_one(order)
    order_id = str(result.inserted_id)

    # Reserve inventory
    reserved = reserve_inventory(items)
    if not reserved:
        mongo.db.orders.update_one({"_id": result.inserted_id}, {"$set": {"order_status": "FAILED"}})
        return jsonify({"status": "FAILED", "reason": "Insufficient stock"}), 409

    # Call payment service
    status, response = PaymentService.add_payment(order_id, totals["total"])
    if status == 201 and response.get("status") == "SUCCESS":
        mongo.db.orders.update_one({"_id": result.inserted_id}, {
            "$set": {"payment_status": "PAID", "order_status": "CONFIRMED"}
        })
        order["order_status"] = "CONFIRMED"
        order["payment_status"] = "PAID"
        order["payment"] = response
    else:
        mongo.db.orders.update_one({"_id": result.inserted_id}, {
            "$set": {"order_status": "CANCELLED", "payment_status": "FAILED"}
        })
        order["order_status"] = "CANCELLED"
        order["payment_status"] = "FAILED"
        order["payment"] = response

    order["_id"] = order_id
    return jsonify(order), 201

@order_bp.route("/v1/orders/<string:order_id>", methods=["GET"])
def get_orders(order_id):
    mongo = current_app.mongo
    order_data = mongo.db.orders.find_one({"_id":ObjectId(order_id)})
    if not order_data:
        return jsonify({"error": "Order not found"}), 404

    order_data["_id"] = str(order_data["_id"])

    return jsonify(order_data), 200


@order_bp.route("/v1/orders/<string:order_id>/cancel", methods=["GET"])
def get(order_id):
    mongo = current_app.mongo
    order_as_mongo_id = ObjectId(order_id)
    order = mongo.db.orders.find_one({"_id": order_as_mongo_id})
    if not order:
        return {"error": "Order not found"}, 404

    status = order.get("order_status")
    if status in ("CANCELLED", "DELIVERED"):
        return {"error": f"cannot cancel order in state {status}"}, 409

    # If there's a payment that succeeded, refund via payment service
    payment_info = order.get("payment_status")
    if payment_info == "PAID":
        status, response = PaymentService.refund_payment(order["_id"])
        if status == 200 and response.get("status") == "SUCCESS":
            mongo.db.orders.update_one({"_id": order_as_mongo_id}, {"$set":{"payment_status": "REFUNDED"}})
        else:
            return jsonify({"message": "Failed to cancel the order."}), 400

    mongo.db.orders.update_one({"_id": order_as_mongo_id}, {"$set": {"order_status": "CANCELLED", "cancelled_at": now_iso()}})
    return {"status": "CANCELLED", "order_id": order_id}, 200

