import pytest
import mongomock
from fastapi.testclient import TestClient
import main  # important: we need to patch main.collection_historial

fake_client = TestClient(main.app)
# Create mock DB and collection
fake_mongo_client = mongomock.MongoClient()
fake_database = fake_mongo_client.practica1
fake_mock_collection = fake_database.historial


@pytest.mark.parametrize(
    "a, b, expected", 
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
        (2.5, 2.5, 5.0),
        (1e10, 1e10, 2e10)
    ]
)
def test_sum_numbers(monkeypatch, a, b, expected):
    monkeypatch.setattr(main, "collection_historial", fake_mock_collection)

    fake_mock_collection.delete_many({})

    response = fake_client.get(f"/calculator/sum?a={a}&b={b}")
    assert response.status_code == 200
    assert response.json() == {"a": a, "b": b, "result": expected}
    
    # ✅ Assert that the record was inserted into mongomock
    saved = fake_mock_collection.find_one({"a": a, "b": b})
    assert saved is not None
    assert saved["result"] == expected

def test_historial(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_mock_collection)

    response = fake_client.get("/calculator/history")
    assert response.status_code == 200

    expected_data = list(fake_mock_collection.find({}))

    historial = []
    for document in expected_data:
        historial.append({
            "a": document.get("a"),
            "b": document.get("b"),
            "result": document.get("result"),
            "date": document["date"].isoformat()
        })

    print(f"DEBUG: expected_data = {historial}")
    print(f"DEBUG: response.json() = {response.json()}")

    assert response.json() == historial