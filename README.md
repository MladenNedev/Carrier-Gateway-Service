# Carrier Gateway Service

## Purpose

Carrier Gateway Service is an internal backend system designed to safely ingest, normalize, and
track shipment data from merchant systems and external carriers.

It focuses on correctness under retries, partial failures, and out-of-order events, which are
common in real-world logistics and integration-heavy systems.

## What problem this service solves

This service prevents the most common shipment data failures in distributed systems:
- Duplicate shipment creation caused by retries or replayed requests
- Invalid or out-of-order shipment status updates
- Retried carrier events corrupting shipment history
- Lack of auditability around shipment state changes

## Who uses this

- Internal platform service used by merchant systems, marketplaces, or ops teams
- Not end-user facing

The included frontend is an internal operations dashboard used to:
- Observe shipments and their lifecycle
- Demonstrate idempotency behavior
- Visualize status transitions and event history

## Core guarantees

- Idempotent shipment creation keyed by `(merchant_id, external_reference)`
- Strict status transitions enforced via a state machine
- Immutable event history (append-only, ordered)

## Why idempotency matters

Retries are normal in distributed systems.

If shipment creation is not idempotent, retries can silently create duplicate shipments,
causing downstream issues in billing, fulfillment, and analytics. This service guarantees
that repeated requests always resolve to the same shipment.

## High-level architecture

API -> Service -> Domain -> Persistence

This separation keeps business rules explicit, testable, and resilient to retries and
integration errors.

- API: HTTP routing and error mapping
- Service: Business orchestration, idempotency, state transitions
- Domain: Entities, enums, invariants
- Persistence: Database models and repositories

## Example real-world flow

1) A merchant submits a shipment creation request.
2) A duplicate request arrives due to retry.
3) The service returns the existing shipment ID instead of creating a duplicate.
4) A carrier event arrives and updates shipment status.
5) All status changes are recorded as immutable events.

## How to demo

1) Create a merchant.
2) Create a shipment with an external_reference.
3) Repeat the same request to observe idempotency.
4) Apply status transitions.
5) Append carrier events and inspect the timeline.

## API example

POST /api/v1/shipments

{
  "merchant_id": "...",
  "external_reference": "ORDER-123",
  "name": "Customer shipment"
}

## Running locally (Docker)

Start backend + frontend:

docker compose up --build

Frontend: `http://localhost:5173`  
API: `http://localhost:8000/docs`

Run tests:

docker compose run --rm -e DATABASE_TEST_URL=postgresql+psycopg://postgres:postgres@db:5432/shipping_db_test -v "$PWD:/app" api pytest

## External Integrations (Adapters)

Adapters model how external carrier or webhook payloads are translated into internal domain events.
- Adapters translate external formats into internal events
- Business rules live in services and domain, not inside adapters
- The current adapter implementation is intentionally minimal and serves as a boundary demonstration

This mirrors how real systems isolate third-party integrations from core business logic.

## Out of scope (by design)

- Authentication and user management
- Async processing / message queues
- Real carrier integrations
- Webhook retry guarantees

These are intentionally excluded to keep the project focused on core backend correctness and
integration boundaries.

## Target level

This project is implemented to reflect production-style backend design, prioritizing
correctness, clarity, and testability over feature breadth.

## Performance note

Shipment event timelines are indexed by `shipment_id` to keep event lookups fast at scale.
