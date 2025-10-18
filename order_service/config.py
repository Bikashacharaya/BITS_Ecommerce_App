import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/order")
    PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:18081")
