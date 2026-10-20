import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(PROJECT_ROOT, "resources", "images")
PRODUCTS_IMG_DIR = os.path.join(IMAGES_DIR, "products")
AVATARS_DIR = os.path.join(IMAGES_DIR, "avatars")
STYLES_DIR = os.path.join(PROJECT_ROOT, "resources", "styles")

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "gourmet_db")
    
    COLL_USERS = "users"
    COLL_PRODUCTS = "products"
    COLL_CATEGORIES = "categories"
    COLL_REVIEWS = "reviews"
    COLL_PRICE_HISTORY = "price_history"
    COLL_CARTS = "carts"
    COLL_FAVORITES = "favorites"