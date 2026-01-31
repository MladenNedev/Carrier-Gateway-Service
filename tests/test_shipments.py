import uuid
from datetime import datetime, timedelta, timezone


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


def _update_status(client, shipment_id, status):
    response = client.post(
        f"/api/v1/shipments/{shipment_id}/status",
        json={"status": status},
    )
    return response


def _add_event(client, shipment_id, event_type, occurred_at):
    payload = {
        "type": event_type,
        "source": "carrier",
        "reason": "test",
        "occurred_at": occurred_at,
    }
    return client.post(f"/api/v1/shipments/{shipment_id}/events", json=payload)


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


def test_update_shipment_status_allowed_transition(client):
    merchant_id = _create_merchant(client)
    shipment = _create_shipment(client, merchant_id, "order-700")

    response = _update_status(client, shipment["id"], "in_transit")
    assert response.status_code == 200
    assert response.json()["status"] == "in_transit"


def test_update_shipment_status_forbidden_transition(client):
    merchant_id = _create_merchant(client)
    shipment = _create_shipment(client, merchant_id, "order-701")

    response = _update_status(client, shipment["id"], "delivered")
    assert response.status_code == 400


def test_update_shipment_status_idempotent(client):
    merchant_id = _create_merchant(client)
    shipment = _create_shipment(client, merchant_id, "order-702")

    first = _update_status(client, shipment["id"], "in_transit")
    assert first.status_code == 200
    second = _update_status(client, shipment["id"], "in_transit")
    assert second.status_code == 200


def test_add_shipment_event_and_list_ordered(client):
    merchant_id = _create_merchant(client)
    shipment = _create_shipment(client, merchant_id, "order-800")

    earlier = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    later = datetime.now(timezone.utc).isoformat()

    first = _add_event(client, shipment["id"], "label_created", earlier)
    assert first.status_code == 200
    second = _add_event(client, shipment["id"], "picked_up", later)
    assert second.status_code == 200

    response = client.get(f"/api/v1/shipments/{shipment['id']}/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 2
    assert events[0]["type"] == "label_created"
    assert events[1]["type"] == "picked_up"


def test_add_shipment_event_missing_shipment_returns_404(client):
    payload = {
        "type": "label_created",
        "source": "carrier",
        "reason": "missing",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post(f"/api/v1/shipments/{uuid.uuid4()}/events", json=payload)
    assert response.status_code == 404


def test_list_shipments_filters_and_paginates(client):
    merchant_a = _create_merchant(client)
    merchant_b = _create_merchant(client)

    shipment_a1 = _create_shipment(client, merchant_a, "order-900")
    shipment_a2 = _create_shipment(client, merchant_a, "order-901")
    shipment_b = _create_shipment(client, merchant_b, "order-902")

    response = client.get(f"/api/v1/shipments?merchant_id={merchant_a}")
    assert response.status_code == 200
    data = response.json()
    ids = {item["id"] for item in data}
    assert shipment_a1["id"] in ids
    assert shipment_a2["id"] in ids
    assert shipment_b["id"] not in ids

    response = client.get(f"/api/v1/shipments?merchant_id={merchant_a}&limit=1&offset=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
