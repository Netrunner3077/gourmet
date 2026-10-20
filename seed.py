"""Заполняет БД базовыми категориями и товарами.
Запускать один раз: python seed.py
"""
from models.database import Database, init_indexes
from models.category_model import CategoryModel
from models.product_model import ProductModel


CATEGORIES = ["Молочные изделия", "Мясные изделия", "Газированные напитки"]

PRODUCTS = [
    ("Молочные изделия", "Молоко «Коровка из Кореновки» 2,5%", "Коровка из Кореновки", "Молоко цельное, молоко обезжиренное. Массовая доля жира 2,5%.", ["Лактоза"], [], ["milk.jpg"], 89.90),
    ("Молочные изделия", "Сыр «Российский»", "Простоквашино", "Молоко нормализованное, соль, закваска, ферментный препарат.", ["Лактоза"], [], ["cheese.jpg"], 179.50),
    ("Молочные изделия", "Творог «Простоквашино» 9%", "Простоквашино", "Молоко нормализованное, закваска. Массовая доля жира 9%.", ["Лактоза"], [], ["cottage_cheese.jpg"], 129.00),
    ("Мясные изделия", "Колбаса «Докторская» (варёная)", "Тавр", "Свинина, говядина, яйца куриные, молоко, соль, нитрит натрия.", ["Яйца", "Лактоза"], ["E250"], ["sausage.jpg"], 219.00),
    ("Мясные изделия", "Шницель из свинины", "Дальние Дали", "Свинина, лук, соль, специи, панировочные сухари.", ["Глютен"], [], ["schnitzel.jpg"], 259.90),
    ("Мясные изделия", "Курица «Цыплёнок-бройлер»", "Белая Птица", "Мясо цыплёнка-бройлера. Замороженное.", [], [], ["chicken.jpg"], 189.00),
    ("Газированные напитки", "Добрый Кола", "Добрый", "Вода газированная, сахар, краситель E150d, кислота ортофосфорная, кофеин, ароматизаторы.", [], ["E150d", "E338"], ["good_kola.jpg"], 79.00),
    ("Газированные напитки", "Bitter", "Bitter", "Вода газированная, сахар, лимонная кислота, натуральные экстракты трав, хинин.", [], ["E330"], ["bitter.jpg"], 89.00),
    ("Газированные напитки", "Квас «Русский Дар»", "Русский Дар", "Вода, сахар, солод ржаной, дрожжи, кислота молочная.", ["Глютен"], [], ["kvas.jpg"], 69.00),
]


def seed():
    db = Database()
    init_indexes()

    cat_model = CategoryModel()
    prod_model = ProductModel()

    if cat_model.count() > 0 or prod_model.count() > 0:
        print("[SEED] База уже наполнена. Очищаю старые записи...")
        db.categories.delete_many({})
        db.products.delete_many({})
        db.reviews.delete_many({})
        db.price_history.delete_many({})

    cat_ids = {}
    for name in CATEGORIES:
        cid = cat_model.create(name)
        cat_ids[name] = cid
        print(f"[SEED] Категория: {name} → {cid}")

    for (cat_name, name, brand, composition, allergens, additives, images, price) in PRODUCTS:
        pid = prod_model.create(
            name=name,
            category_id=cat_ids[cat_name],
            brand=brand,
            composition=composition,
            allergens=allergens,
            additives=additives,
            images=images,
            current_price=price,
        )
        print(f"[SEED] Товар: {name} → {pid}")

    print(f"\n✅ Готово: {len(cat_ids)} категорий, {len(PRODUCTS)} товаров.")


if __name__ == "__main__":
    seed()