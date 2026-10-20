import json
import os
import re
from config import PROJECT_ROOT


DATA_DIR = os.path.join(PROJECT_ROOT, "resources", "data")

_E_RE = re.compile(r"\bE\s?(\d{3,4})([a-zа-я]?)\b", re.IGNORECASE)

_ADDITIVES = None
_ALLERGENS = None


def _load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_additives():
    global _ADDITIVES
    if _ADDITIVES is None:
        _ADDITIVES = _load_json("additives.json")
    return _ADDITIVES


def _get_allergens():
    global _ALLERGENS
    if _ALLERGENS is None:
        _ALLERGENS = _load_json("allergens.json")
    return _ALLERGENS


def _normalize(text):
    return text.lower().replace("ё", "е")


def _find_additives(text):
    found = {}
    for m in _E_RE.finditer(text):
        suffix = m.group(2).lower() if m.group(2) else ""
        code = f"E{m.group(1)}{suffix}"

        if code in found:
            continue

        meta = _get_additives().get(code)
        if meta:
            found[code] = {
                "code": code,
                "name": meta["name"],
                "risk": meta["risk"],
                "category": meta.get("category", "—"),
                "note": meta.get("note", ""),
            }
        else:
            found[code] = {
                "code": code,
                "name": "неизвестная добавка",
                "risk": 2,
                "category": "—",
                "note": "",
            }
    return sorted(found.values(), key=lambda x: (-x["risk"], x["code"]))


def _find_allergens(text):
    norm = _normalize(text)
    found = []
    for allergen, synonyms in _get_allergens().items():
        for syn in synonyms:
            if _normalize(syn) in norm:
                found.append({"name": allergen, "matched": syn})
                break
    return found


def _risk_level(additives, allergens):
    if not additives and not allergens:
        return "low", 0, "#047857"

    max_risk = max((a["risk"] for a in additives), default=0)
    avg_risk = sum(a["risk"] for a in additives) / len(additives) if additives else 0
    has_high = any(a["risk"] >= 4 for a in additives)

    score = max_risk + (1 if allergens else 0) + (1 if len(additives) > 5 else 0)

    if has_high or score >= 6:
        return "high", score, "#B91C1C"
    if max_risk >= 3 or allergens or avg_risk >= 2.5:
        return "medium", score, "#B45309"
    return "low", score, "#047857"


def analyze(composition):
    if not composition or not composition.strip():
        return {
            "additives": [],
            "allergens": [],
            "risk_level": "low",
            "risk_label": "Нет данных",
            "risk_color": "#64748B",
            "score": 0,
        }

    additives = _find_additives(composition)
    allergens = _find_allergens(composition)
    level, score, color = _risk_level(additives, allergens)

    label_map = {
        "low": "Низкий риск",
        "medium": "Средний риск",
        "high": "Высокий риск",
    }

    return {
        "additives": additives,
        "allergens": allergens,
        "risk_level": level,
        "risk_label": label_map[level],
        "risk_color": color,
        "score": score,
    }