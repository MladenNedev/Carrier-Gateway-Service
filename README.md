# Carrier Gateway Service

Production-grade FastAPI service for merchant-managed shipments with idempotent creation, status transitions, and event ingestion.

## Architecture

Layers:
- API: `app/api/v1/*`
- Service: `app/services/*`
- Domain: `app/domain/*`
- Persistence: `app/persistence/*`
- Schemas: `app/schemas/*`

Request flow:
API route -> service -> repository -> database; domain models are returned and serialized by schemas.

## Run locally (Docker)

```bash
docker compose up --build
```

## Migrations

Initialize/update schema:
```bash
docker compose run --rm -e DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/shipping_db api alembic upgrade head
```

## Tests

Create test DB once:
```bash
docker compose exec db psql -U postgres -c "CREATE DATABASE shipping_db_test;"
```

Run tests:
```bash
docker compose build api
docker compose run --rm -e DATABASE_TEST_URL=postgresql+psycopg://postgres:postgres@db:5432/shipping_db_test api pytest
```

## Idempotency contract

`POST /api/v1/shipments` is idempotent by `(merchant_id, external_reference)`.
- If a shipment already exists for the pair, the API returns `200` and the existing shipment.
- If it does not exist, the API returns `201` and creates a new shipment.

`external_reference` is required.

## Example requests

Create a merchant:
```bash
curl -X POST http://localhost:8000/api/v1/merchant \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme"}'
```

Create a shipment:
```bash
curl -X POST http://localhost:8000/api/v1/shipments \
  -H "Content-Type: application/json" \
  -d '{"merchant_id":"<uuid>","name":"Order 123","external_reference":"order-123"}'
```

Update shipment status:
```bash
curl -X POST http://localhost:8000/api/v1/shipments/<id>/status \
  -H "Content-Type: application/json" \
  -d '{"status":"in_transit"}'
```

Add shipment event:
```bash
curl -X POST http://localhost:8000/api/v1/shipments/<id>/events \
  -H "Content-Type: application/json" \
  -d '{"type":"picked_up","source":"carrier","occurred_at":"2024-01-01T12:00:00Z"}'
```
