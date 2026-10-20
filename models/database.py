from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config


class Database:
    """Singleton-обёртка над MongoClient."""
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            self._client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=3000)
            self._client.admin.command("ping")
            print("[DB] Подключение к MongoDB установлено.")
        except ConnectionFailure as e:
            raise RuntimeError(f"Не удалось подключиться к MongoDB: {e}")

    @property
    def db(self):
        return self._client[Config.DB_NAME]

    @property
    def users(self):
        return self.db[Config.COLL_USERS]

    @property
    def products(self):
        return self.db[Config.COLL_PRODUCTS]

    @property
    def categories(self):
        return self.db[Config.COLL_CATEGORIES]

    @property
    def reviews(self):
        return self.db[Config.COLL_REVIEWS]

    @property
    def price_history(self):
        return self.db[Config.COLL_PRICE_HISTORY]

    @property
    def carts(self):
        return self.db[Config.COLL_CARTS]

    @property
    def favorites(self):
        return self.db[Config.COLL_FAVORITES]

    def close(self):
        if self._client:
            self._client.close()


def init_indexes():
    """Создаёт уникальные индексы и индексы поиска. Вызывать при первом запуске."""
    db = Database()
    db.users.create_index("login", unique=True)
    db.products.create_index([("name", "text"), ("brand", "text")])
    db.reviews.create_index("product_id")
    db.reviews.create_index("user_id")
    print("[DB] Индексы созданы.")