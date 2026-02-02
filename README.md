# Carrier Gateway Service

## What problem this service solves

This service prevents the most common shipment data failures in real systems:
- Duplicate shipment creation from retries or replayed requests
- Inconsistent status updates from out-of-order signals
- Retried carrier events that must not corrupt history
- Lack of auditability for shipment state changes

## Who uses this

- Internal platform service used by merchant systems and marketplaces
- Not end-user facing

This frontend represents an internal operations dashboard for merchant shipment systems.

## Core guarantees

- Idempotent shipment creation by `(merchant_id, external_reference)`
- Strict status transitions (state machine enforced)
- Immutable event history (append-only)

## High-level architecture

API -> Service -> Domain -> Persistence

This structure exists to keep business rules explicit, testable, and correct under retries and concurrency.

## Example real-world flow

1) A merchant submits a shipment request.
2) A duplicate request arrives due to retry.
3) The service returns the existing shipment ID.
4) A carrier event arrives and updates shipment status while preserving history.
