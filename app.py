from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Sampel cart data
user_carts = {}

# URL
PRODUCT_SERVICE_URL = "http://127.0.0.1:5000/products"

def get_product(product_id):
  response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")
  if response.status_code == 200:
    return response.json().get('product')
  return None

# Endpoint to retrieve the cart for a specific user
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart = user_carts.get(user_id, [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return jsonify({"user_id": user_id, "cart": cart, "total_price": total_price})

# Endpoint to add a product to a user's cart
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    product = get_product(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    quantity = request.json.get('quantity', 1)  # Default quantity is 1 if not provided
    cart = user_carts.get(user_id, [])

    # Check if the product is already in the cart
    existing_product = next((item for item in cart if item['id'] == product_id), None)
    if existing_product:
        existing_product['quantity'] += quantity
    else:
        product['quantity'] = quantity
        cart.append(product)

    user_carts[user_id] = cart
    return jsonify({"message": "Product added to cart", "cart": cart}), 200

# Endpoint to remove a product or reduce its quantity from a user's cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    quantity = request.json.get('quantity', 1)  # Default quantity to remove is 1 if not provided
    cart = user_carts.get(user_id, [])

    product = next((item for item in cart if item['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found in cart"}), 404

    # Update the quantity or remove the product if quantity becomes zero
    if product['quantity'] <= quantity:
        cart.remove(product)
    else:
        product['quantity'] -= quantity

    user_carts[user_id] = cart
    return jsonify({"message": "Product removed from cart", "cart": cart}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)