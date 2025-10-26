from flask import Flask
from api.routes import product_bp

app = Flask(__name__)

# Register Blueprint
app.register_blueprint(product_bp, url_prefix='/v1')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=18082, debug=True)
