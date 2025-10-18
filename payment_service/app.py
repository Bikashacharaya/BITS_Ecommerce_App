from flask import Flask
from flask_pymongo import PyMongo
from config import Config
from api.route import payment_bp

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
app.mongo = mongo

app.register_blueprint(payment_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=18081, debug=True)
