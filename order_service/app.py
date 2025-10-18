from flask import Flask
from flask_pymongo import PyMongo
from config import Config
from api.route import order_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize MongoDB
mongo = PyMongo(app)
app.mongo = mongo

# Register blueprint
app.register_blueprint(order_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=18080, debug=True)
