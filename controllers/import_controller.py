import os
import re
import requests

from config import PRODUCTS_IMG_DIR
from models.product_model import ProductModel
from models.category_model import CategoryModel
from utils.openfoodfacts_parser import OpenFoodFactsClient
from utils.time_utils import utcnow


CATEGORY_KEYWORDS = {
    "Молочные изделия": [
        "молоко", "молочн", "сыр", "творог", "йогурт", "кефир",
        "сметана", "сливк", "масло сливочное", "dairy", "milk",
        "cheese", "yogurt", "kefir",
    ],
    "Мясные изделия": [
        "мясо", "мясн", "колбас", "сосиск", "курица", "свинин",
        "говядин", "шницель", "ветчин", "meat", "sausage", "chicken",
        "pork", "beef",
    ],
    "Газированные напитки": [
        "напиток", "газирован", "кола", "лимонад", "квас", "сок",
        "drink", "soda", "cola", "beverage", "juice",
    ],
}


class ImportController:
    def __init__(self):
        self.client = OpenFoodFactsClient()
        self.products = ProductModel()
        self.categories = CategoryModel()

    def search(self, query: str, limit: int = 20) -> list[dict]:
        if not query.strip():
            return []
        return self.client.search_by_name(query.strip(), limit=limit)

    def get_by_barcode(self, barcode: str) -> dict | None:
        barcode = barcode.strip()
        if not barcode:
            return None
        return self.client.get_by_barcode(barcode)

    def guess_category_id(self, remote_product: dict):
        text = " ".join(
            [remote_product.get("name", "")]
            + remote_product.get("categories", [])
        ).lower()

        for cat_name, keywords in CATEGORY_KEYWORDS.items():
            if any(k in text for k in keywords):
                cat = self.categories.get_by_name(cat_name)
                if cat:
                    return cat["_id"]

        all_cats = self.categories.get_all()
        return all_cats[0]["_id"] if all_cats else None

    def import_product(self, remote: dict, category_id, price: float = 0.0, download_image: bool = True) -> tuple[bool, str]:
        if not remote or not remote.get("name"):
            return False, "Нет данных о товаре."

        existing = self.products.find_by_name(remote["name"])
        if existing:
            return False, f"Товар «{remote['name']}» уже есть в базе."

        image_filename = None
        if download_image and remote.get("image_url"):
            image_filename = self._download_image(
                remote["image_url"], remote["name"]
            )

        try:
            self.products.create(
                name=remote["name"],
                category_id=category_id,
                brand=remote.get("brand", "—"),
                composition=remote.get("composition", ""),
                allergens=remote.get("allergens", []),
                additives=remote.get("additives", []),
                images=[image_filename] if image_filename else [],
                current_price=float(price),
            )
            return True, f"Товар «{remote['name']}» импортирован."
        except Exception as e:
            return False, f"Ошибка сохранения: {e}"

    def _download_image(self, url: str, product_name: str) -> str | None:
        if not url.startswith(("http://", "https://")):
            return None

        try:
            r = requests.get(
                url, timeout=15, stream=True,
                headers={"User-Agent": "Gourmet/1.0 (educational)"}
            )
            r.raise_for_status()
        except Exception:
            return None

        content_type = r.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            return None

        content = b""
        try:
            for chunk in r.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > 5 * 1024 * 1024:
                    return None
        except Exception:
            return None

        safe = re.sub(
            r"[^\w\-]+", "_", product_name.lower(), flags=re.UNICODE
        ).strip("_")[:60]
        if not safe:
            safe = "off_" + utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{safe}.jpg"

        os.makedirs(PRODUCTS_IMG_DIR, exist_ok=True)
        path = os.path.join(PRODUCTS_IMG_DIR, filename)

        try:
            with open(path, "wb") as f:
                f.write(content)
            return filename
        except Exception:
            return None