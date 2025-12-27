from app.core.models import UnifiedData, ETLRun
from datetime import datetime, timezone

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["db_connected"] is True

def test_data_endpoint_pagination(client, db):
    # Seed some data
    for i in range(15):
        db.add(UnifiedData(
            source="test",
            external_id=f"ext_{i}",
            title=f"Title {i}",
            description=f"Desc {i}",
            data={}
        ))
    db.commit()
    
    # Test first page
    response = client.get("/api/v1/data?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 10
    
    # Test second page
    response = client.get("/api/v1/data?skip=10&limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 5

def test_stats_endpoint(client, db):
    # Seed some ETL run stats
    db.add(ETLRun(
        run_id="run_1",
        source="api_source",
        status="success",
        records_processed=100,
        duration_ms=500.0,
        started_at=datetime.now(timezone.utc)
    ))
    db.commit()
    
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["source"] == "api_source"
    assert data[0]["records_processed"] == 100

def test_api_latency_headers(client):
    response = client.get("/api/v1/health")
    assert "X-API-Latency-MS" in response.headers
    assert "X-Request-ID" in response.headers
