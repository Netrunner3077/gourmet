from utils.composition_analyzer import analyze


def test_empty_composition():
    result = analyze("")
    assert result["additives"] == []
    assert result["allergens"] == []
    assert result["risk_level"] == "low"


def test_none_composition():
    result = analyze(None)
    assert result["risk_level"] == "low"


def test_single_additive():
    result = analyze("Вода, сахар, E330")
    codes = [a["code"] for a in result["additives"]]
    assert "E330" in codes


def test_additive_with_suffix():
    result = analyze("Краситель E150d")
    codes = [a["code"] for a in result["additives"]]
    assert "E150d" in codes


def test_high_risk_additive():
    result = analyze("Свинина, соль, E250")
    assert result["risk_level"] == "high"
    codes = [a["code"] for a in result["additives"]]
    assert "E250" in codes


def test_unknown_additive_detected():
    result = analyze("E9999")
    codes = [a["code"] for a in result["additives"]]
    assert "E9999" in codes


def test_allergen_lactose():
    result = analyze("Молоко цельное, закваска")
    names = [a["name"] for a in result["allergens"]]
    assert "Лактоза" in names


def test_allergen_gluten():
    result = analyze("Мука пшеничная, соль")
    names = [a["name"] for a in result["allergens"]]
    assert "Глютен" in names


def test_allergen_eggs():
    result = analyze("Яйца куриные, соль")
    names = [a["name"] for a in result["allergens"]]
    assert "Яйца" in names


def test_case_insensitive():
    r1 = analyze("МОЛОКО")
    r2 = analyze("молоко")
    assert len(r1["allergens"]) == len(r2["allergens"])


def test_additives_sorted_by_risk():
    result = analyze("E330, E250, E102")
    risks = [a["risk"] for a in result["additives"]]
    assert risks == sorted(risks, reverse=True)


def test_clean_composition_no_risk():
    result = analyze("Вода, соль")
    assert result["risk_level"] == "low"
    assert result["additives"] == []
    assert result["allergens"] == []