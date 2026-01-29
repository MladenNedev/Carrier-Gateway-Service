import uuid


def test_create_shipment_idempotent_returns_existing(client):
    merchant_name = f"merchant-{uuid.uuid4()}"
    merchant_resp = client.post(
        "/api/v1/merchant",
        json={"name": merchant_name},
    )
    assert merchant_resp.status_code == 200
    merchant_id = merchant_resp.json()["id"]

    payload = {
        "merchant_id": merchant_id,
        "name": "Order 123",
        "external_reference": "order-123",
    }
    first = client.post("/api/v1/shipments", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/shipments", json=payload)
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


def test_create_shipment_missing_merchant_returns_404(client):
    payload = {
        "merchant_id": str(uuid.uuid4()),
        "name": "Missing Merchant",
        "external_reference": "order-404",
    }
    response = client.post("/api/v1/shipments", json=payload)
    assert response.status_code == 404
