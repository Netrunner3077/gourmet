import requests


API_BASE = "https://world.openfoodfacts.org"
USER_AGENT = "Gourmet/1.0 (educational project)"


class OpenFoodFactsClient:
    def __init__(self, timeout: int = 12):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def get_by_barcode(self, barcode: str) -> dict | None:
        url = f"{API_BASE}/api/v0/product/{barcode}.json"
        try:
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, ValueError):
            return None

        if data.get("status") != 1 or "product" not in data:
            return None
        return self._normalize(data["product"])

    def search_by_name(self, query: str, limit: int = 20, country: str = "russia") -> list[dict]:
        url = f"{API_BASE}/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": limit,
            "fields": (
                "code,product_name,product_name_ru,brands,"
                "ingredients_text,ingredients_text_ru,"
                "additives_tags,allergens_tags,image_url,"
                "categories_tags,quantity,nutriscore_grade"
            ),
        }
        if country:
            params["tagtype_0"] = "countries"
            params["tag_contains_0"] = "contains"
            params["tag_0"] = country

        try:
            r = self.session.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, ValueError):
            return []

        products = data.get("products", [])
        result = []
        for p in products:
            normalized = self._normalize(p)
            if normalized and normalized["name"]:
                result.append(normalized)
        return result

    def _normalize(self, raw: dict) -> dict | None:
        if not raw:
            return None

        name = (
            raw.get("product_name_ru")
            or raw.get("product_name")
            or ""
        ).strip()
        if not name:
            return None

        composition = (
            raw.get("ingredients_text_ru")
            or raw.get("ingredients_text")
            or ""
        ).strip()

        brand = (raw.get("brands") or "").split(",")[0].strip()

        additives = self._parse_additives(raw.get("additives_tags", []))
        allergens = self._parse_allergens(raw.get("allergens_tags", []))
        categories = self._parse_categories(raw.get("categories_tags", []))

        return {
            "barcode": raw.get("code", ""),
            "name": name,
            "brand": brand or "—",
            "composition": composition or "Состав не указан.",
            "additives": additives,
            "allergens": allergens,
            "categories": categories,
            "image_url": raw.get("image_url", "") or raw.get("image_front_url", ""),
            "quantity": raw.get("quantity", ""),
            "nutriscore": raw.get("nutriscore_grade", ""),
        }

    def _parse_additives(self, tags: list) -> list[str]:
        result = []
        for t in tags:
            code = t.split(":")[-1].upper()
            if code and code not in result:
                result.append(code)
        return result

    def _parse_allergens(self, tags: list) -> list[str]:
        mapping = {
            "en:gluten": "Глютен",
            "en:milk": "Лактоза",
            "en:eggs": "Яйца",
            "en:soybeans": "Соя",
            "en:nuts": "Орехи",
            "en:peanuts": "Орехи",
            "en:fish": "Рыба и морепродукты",
            "en:crustaceans": "Рыба и морепродукты",
            "en:molluscs": "Рыба и морепродукты",
            "en:mustard": "Горчица",
            "en:celery": "Сельдерей",
            "en:sesame-seeds": "Кунжут",
            "en:sulphur-dioxide-and-sulphites": "Сульфиты",
        }
        result = []
        for t in tags:
            ru = mapping.get(t, None)
            if ru and ru not in result:
                result.append(ru)
        return result

    def _parse_categories(self, tags: list) -> list[str]:
        result = []
        for t in tags:
            name = t.split(":")[-1].replace("-", " ")
            if name and name not in result:
                result.append(name)
        return result