from unittest.mock import patch, MagicMock
from utils.openfoodfacts_parser import OpenFoodFactsClient


@patch("requests.Session.get")
def test_get_by_barcode_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "code": "123456",
            "product_name_ru": "Тестовый сыр",
            "brands": "Мой Бренд",
            "ingredients_text_ru": "Молоко, соль",
            "additives_tags": ["en:e330"],
            "allergens_tags": ["en:milk"],
            "categories_tags": ["en:dairies"]
        }
    }
    mock_get.return_value = mock_response

    client = OpenFoodFactsClient()
    result = client.get_by_barcode("123456")
    
    assert result is not None
    assert result["name"] == "Тестовый сыр"
    assert result["brand"] == "Мой Бренд"
    assert "E330" in result["additives"]
    assert "Лактоза" in result["allergens"]


@patch("requests.Session.get")
def test_get_by_barcode_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": 0}
    mock_get.return_value = mock_response

    client = OpenFoodFactsClient()
    result = client.get_by_barcode("000000")
    assert result is None


@patch("requests.Session.get")
def test_search_by_name(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "products": [
            {"product_name": "Молоко", "brands": "Домик в деревне"},
            {"product_name": "", "brands": "Пустое имя"}
        ]
    }
    mock_get.return_value = mock_response

    client = OpenFoodFactsClient()
    results = client.search_by_name("молоко")
    
    assert len(results) == 1
    assert results[0]["name"] == "Молоко"