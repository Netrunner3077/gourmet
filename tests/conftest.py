import os

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/")

import pytest

from config import Config
Config.DB_NAME = "gourmet_test_db"

from models.database import Database
from utils.session import Session


COLLECTIONS = [
    "users", "categories", "products", "reviews",
    "price_history", "carts", "favorites",
]


@pytest.fixture(scope="session", autouse=True)
def _setup_test_db():
    db = Database()
    db._client.drop_database("gourmet_test_db")
    yield
    db._client.drop_database("gourmet_test_db")


@pytest.fixture(autouse=True)
def _clean_collections():
    db = Database()
    for coll in COLLECTIONS:
        db.db[coll].delete_many({})
    Session.logout()
    yield


@pytest.fixture
def user_model():
    from models.user_model import UserModel
    return UserModel()


@pytest.fixture
def category_model():
    from models.category_model import CategoryModel
    return CategoryModel()


@pytest.fixture
def product_model():
    from models.product_model import ProductModel
    return ProductModel()


@pytest.fixture
def review_model():
    from models.review_model import ReviewModel
    return ReviewModel()


@pytest.fixture
def cart_model():
    from models.cart_model import CartModel
    return CartModel()


@pytest.fixture
def favorite_model():
    from models.favorite_model import FavoriteModel
    return FavoriteModel()


@pytest.fixture
def sample_category(category_model):
    cid = category_model.create("Тестовая категория")
    return cid


@pytest.fixture
def sample_user(user_model):
    uid = user_model.create_user("tester", "pass1234")
    user = user_model.get_by_id(uid)
    Session.set_user(user)
    return user


@pytest.fixture
def sample_product(product_model, sample_category):
    pid = product_model.create(
        name="Тестовый товар",
        category_id=sample_category,
        brand="TestBrand",
        composition="Молоко, сахар, E250, E330",
        allergens=["Лактоза"],
        additives=["E250"],
        images=[],
        current_price=100.0,
    )
    return pid