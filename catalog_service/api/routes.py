from flask import Blueprint, request, jsonify
from api.actions import (
    create_product,
    get_all_products,
    get_product_by_id,
    update_product,
    delete_product
)

product_bp = Blueprint('product', __name__)

# CREATE
@product_bp.route('/product', methods=['POST'])
def create():
    data = request.json
    new_id = create_product(data)
    return jsonify({'message': 'Product created', 'product_id': new_id}), 201


# READ ALL
@product_bp.route('/products', methods=['GET'])
def get_all():
    filters = {
        'name': request.args.get('name'),
        'category': request.args.get('category'),
        'price': request.args.get('price'),
        'is_active': request.args.get('is_active')
    }
    products = get_all_products(filters)
    return jsonify(products)


# READ ONE
@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_one(product_id):
    product = get_product_by_id(product_id)
    if product:
        return jsonify(product)
    return jsonify({'message': 'Product not found'}), 404


# UPDATE
@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update(product_id):
    data = request.json
    rows = update_product(product_id, data)
    if rows == 0:
        return jsonify({'message': 'Product not found'}), 404
    return jsonify({'message': 'Product updated'})


# DELETE
@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete(product_id):
    rows = delete_product(product_id)
    if rows == 0:
        return jsonify({'message': 'Product not found'}), 404
    return jsonify({'message': f'Product {product_id} deleted'})
