import logging

from fastapi.testclient import TestClient

from app.api.main import app


def test_health_logs_structured_request_metadata(
    caplog,
) -> None:
    client = TestClient(app)

    with caplog.at_level(
        logging.INFO,
        logger="decisionai",
    ):
        response = client.get("/health")

    assert response.status_code == 200

    matching_records = [
        record
        for record in caplog.records
        if (record.name == "decisionai" and "path=/health" in record.getMessage())
    ]

    assert len(matching_records) == 1

    message = matching_records[0].getMessage()

    assert "request_id=" in message

    assert "method=GET" in message

    assert "path=/health" in message

    assert "status_code=200" in message

    assert "duration_ms=" in message
