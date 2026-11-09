from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """
    Sanity check that the app boots and routes work. Expand this test
    directory as each module (auth, goals, transactions) is built —
    see Week 10 in the roadmap for the dedicated testing pass.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
