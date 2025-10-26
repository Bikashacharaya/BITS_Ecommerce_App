from flask import Flask
from api.routes import inventory_bp

app = Flask(__name__)

app.register_blueprint(inventory_bp, url_prefix="/v1/inventory")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=18083, debug=True)
