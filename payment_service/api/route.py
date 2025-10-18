from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app
from api.actions import process_payment

payment_bp = Blueprint('payments', __name__)


@payment_bp.route("/v1/payments/charge", methods=["POST"])
def charge():
    data = request.json
    order_id = data.get("order_id")
    amount = data.get("amount")
    method = data.get("method", "CARD")

    if not order_id or not amount:
        return jsonify({"error": "order_id and amount are required"}), 400

    payment = process_payment(order_id, amount, method)
    mongo = current_app.mongo
    inserted = mongo.db.payments.insert_one(payment)
    payment["_id"] = str(inserted.inserted_id)

    return jsonify(payment), 201


@payment_bp.route("/v1/payments/<string:payment_id>", methods=["GET"])
def list_payments(payment_id):
    mongo = current_app.mongo
    payment_detail = mongo.db.payments.find_one({"payment_id": payment_id})
    if not payment_detail:
        return jsonify({"error": "payment not found"}), 404

    payment_detail["_id"] = str(payment_detail["_id"])

    return jsonify(payment_detail), 200


@payment_bp.route("/v1/payments/<string:order_id>/refund", methods=["GET"])
def refund(order_id):
    mongo = current_app.mongo
    payment_detail = mongo.db.payments.find_one({"order_id": order_id})
    if not payment_detail:
        return jsonify({"error": "payment not found"}), 404

    mongo.db.payments.update_one({"order_id": order_id}, {"$set": {"refunded": True}})

    return jsonify(payment_detail), 200
