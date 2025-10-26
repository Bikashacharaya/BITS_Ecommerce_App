# api/routes.py

from flask import Blueprint
from api.actions import (
    get_inventory, reserve_stock, release_stock, ship_stock, low_stock
)

inventory_bp = Blueprint("inventory_bp", __name__)

inventory_bp.route("/", methods=["GET"])(get_inventory)
inventory_bp.route("/reserve", methods=["POST"])(reserve_stock)
inventory_bp.route("/release", methods=["POST"])(release_stock)
inventory_bp.route("/ship", methods=["POST"])(ship_stock)
inventory_bp.route("/low-stock", methods=["GET"])(low_stock)
