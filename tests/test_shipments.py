import uuid


def _create_merchant(client):
    merchant_name = f"merchant-{uuid.uuid4()}"
    response = client.post("/api/v1/merchant", json={"name": merchant_name})
    assert response.status_code == 200
    return response.json()["id"]


def _create_shipment(client, merchant_id, external_reference):
    payload = {
        "merchant_id": merchant_id,
        "name": "Order 123",
        "external_reference": external_reference,
    }
    response = client.post("/api/v1/shipments", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_shipment_idempotent_returns_existing(client):
    merchant_id = _create_merchant(client)

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


def test_create_shipment_missing_external_reference_returns_422(client):
    merchant_id = _create_merchant(client)
    payload = {
        "merchant_id": merchant_id,
        "name": "Order Missing Ref",
    }
    response = client.post("/api/v1/shipments", json=payload)
    assert response.status_code == 422


def test_list_shipments_returns_created(client):
    merchant_id = _create_merchant(client)
    shipment = _create_shipment(client, merchant_id, "order-555")

    response = client.get("/api/v1/shipments")
    assert response.status_code == 200
    data = response.json()
    assert any(item["id"] == shipment["id"] for item in data)


def test_get_shipment_by_id(client):
    merchant_id = _create_merchant(client)
    shipment = _create_shipment(client, merchant_id, "order-556")

    response = client.get(f"/api/v1/shipments/{shipment['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == shipment["id"]
    assert data["merchant_id"] == shipment["merchant_id"]


def test_get_shipment_missing_returns_404(client):
    response = client.get(f"/api/v1/shipments/{uuid.uuid4()}")
    assert response.status_code == 404
