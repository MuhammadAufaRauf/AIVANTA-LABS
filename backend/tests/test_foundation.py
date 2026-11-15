from fastapi.testclient import TestClient

from app.main import app


def test_health_reports_database_connection() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_company_configuration_is_seeded() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/company")
    assert response.status_code == 200
    assert response.json()["company_name"] == "Aivanta Labs"
    assert response.json()["product_name"] == "Aivanta OS"
