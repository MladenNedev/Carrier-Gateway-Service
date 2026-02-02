import { useEffect, useMemo, useState } from "react";
import { api } from "./api.js";

const STATUS_ORDER = [
  "created",
  "in_transit",
  "delivered",
  "failed",
  "cancelled",
];

const STATUS_TRANSITIONS = {
  created: ["in_transit", "cancelled"],
  in_transit: ["delivered", "failed", "cancelled"],
  delivered: [],
  failed: [],
  cancelled: [],
};

const EVENT_TYPES = [
  "label_created",
  "picked_up",
  "out_for_delivery",
  "delivered",
  "delivery_failed",
];

export default function App() {
  const [view, setView] = useState("shipments");
  const [merchants, setMerchants] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [events, setEvents] = useState([]);
  const [lastEventId, setLastEventId] = useState(null);
  const [filters, setFilters] = useState({
    merchant_id: "",
    status: "",
  });
  const [merchantForm, setMerchantForm] = useState({ name: "" });
  const [merchantResult, setMerchantResult] = useState(null);
  const [createForm, setCreateForm] = useState({
    merchant_id: "",
    name: "",
    external_reference: "",
  });
  const [createResult, setCreateResult] = useState(null);
  const [eventForm, setEventForm] = useState({
    type: "label_created",
    source: "carrier",
    occurred_at: "",
    reason: "",
  });
  const [statusUpdate, setStatusUpdate] = useState(null);

  const loadMerchants = async () => {
    const res = await api.getMerchants();
    if (res.ok) setMerchants(res.body);
  };

  useEffect(() => {
    loadMerchants();
  }, []);

  const merchantOptions = useMemo(
    () => merchants.map((m) => ({ id: m.id, name: m.name })),
    [merchants],
  );

  const loadShipments = async () => {
    const params = {};
    if (filters.merchant_id) params.merchant_id = filters.merchant_id;
    if (filters.status) params.status = filters.status;
    const res = await api.getShipments(params);
    if (res.ok) setShipments(res.body);
  };

  const loadShipmentDetail = async (shipmentId) => {
    const res = await api.getShipment(shipmentId);
    if (res.ok) {
      setSelectedShipment(res.body);
      const eventsRes = await api.listEvents(shipmentId);
      if (eventsRes.ok) setEvents(eventsRes.body);
      setView("detail");
    }
  };

  const handleCreateShipment = async (e) => {
    e.preventDefault();
    setCreateResult(null);
    const res = await api.createShipment(createForm);
    if (res.ok) {
      setCreateResult({
        id: res.body.id,
        created: res.status === 201,
      });
    } else if (res.body?.error) {
      setCreateResult({ error: res.body.error.message });
    }
  };

  const handleCreateMerchant = async (e) => {
    e.preventDefault();
    setMerchantResult(null);
    const res = await api.createMerchant(merchantForm);
    if (res.ok) {
      setMerchantResult({ name: res.body.name, id: res.body.id });
      setMerchantForm({ name: "" });
      await loadMerchants();
    } else if (res.body?.error) {
      setMerchantResult({ error: res.body.error.message });
    }
  };

  const handleStatusChange = async (newStatus) => {
    if (!selectedShipment) return;
    const res = await api.updateShipmentStatus(selectedShipment.id, newStatus);
    if (res.ok) {
      setSelectedShipment(res.body);
      setStatusUpdate({ ok: true, status: newStatus });
    } else if (res.body?.error) {
      setStatusUpdate({ ok: false, message: res.body.error.message });
    }
  };

  const handleAddEvent = async (e) => {
    e.preventDefault();
    if (!selectedShipment) return;
    const payload = {
      type: eventForm.type,
      source: eventForm.source,
      reason: eventForm.reason || null,
      occurred_at: eventForm.occurred_at || null,
    };
    const res = await api.addEvent(selectedShipment.id, payload);
    if (res.ok) {
      const eventsRes = await api.listEvents(selectedShipment.id);
      if (eventsRes.ok) setEvents(eventsRes.body);
      setEventForm({ ...eventForm, reason: "", occurred_at: "" });
      setLastEventId(res.body.id);
      setTimeout(() => {
        document.getElementById("event-timeline")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 0);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Carrier Gateway Ops</h1>
          <p>
            This frontend represents an internal operations dashboard for
            merchant shipment systems.
          </p>
        </div>
        <nav className="nav">
          <button
            className={view === "merchants" ? "active" : ""}
            onClick={() => setView("merchants")}
          >
            Merchants
          </button>
          <button
            className={view === "shipments" ? "active" : ""}
            onClick={() => setView("shipments")}
          >
            Shipments
          </button>
          <button
            className={view === "create" ? "active" : ""}
            onClick={() => setView("create")}
          >
            Create Shipment
          </button>
        </nav>
      </header>

      <main className="content">
        <section className="panel demo-flow">
          <h2>Demo Flow</h2>
          <ol>
            <li>Create a merchant</li>
            <li>Create a shipment</li>
            <li>Submit the same external reference again</li>
            <li>Change shipment status</li>
            <li>Add events and observe the timeline</li>
          </ol>
        </section>

        {view === "merchants" && (
          <section className="panel">
            <h2>Merchants</h2>
            <p className="muted">
              Merchants are the root of shipment ownership. Start here.
            </p>
            <form className="form" onSubmit={handleCreateMerchant}>
              <label>
                Name
                <input
                  value={merchantForm.name}
                  onChange={(e) =>
                    setMerchantForm({ name: e.target.value })
                  }
                  required
                />
              </label>
              <span className="hint">
                Merchants own shipments. You must create a merchant before
                creating shipments.
              </span>
              <button type="submit">Create Merchant</button>
            </form>
            {merchantResult && (
              <div className="result">
                {merchantResult.error ? (
                  <p className="error">{merchantResult.error}</p>
                ) : (
                  <>
                    <p>✅ Merchant created</p>
                    <p className="muted">Name: {merchantResult.name}</p>
                    <p className="muted">Merchant ID: {merchantResult.id}</p>
                  </>
                )}
              </div>
            )}
            {merchantOptions.length === 0 ? (
              <div className="empty-state centered">
                <h3>No merchants yet</h3>
                <p>
                  Shipments are always owned by a merchant. Create or seed a
                  merchant to begin.
                </p>
              </div>
            ) : (
              <ul className="list">
                {merchantOptions.map((m) => (
                  <li key={m.id}>
                    <strong>{m.name}</strong>
                    <span className="muted">{m.id}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        {view === "shipments" && (
          <section className="panel">
            <div className="panel-header">
              <h2>Shipments</h2>
              <button onClick={loadShipments}>Refresh</button>
            </div>
            <p className="muted">
              Shipments are idempotent on creation, follow strict status
              transitions, and keep an immutable event history.
            </p>
            <div className="filters">
              <label>
                Merchant
                <select
                  value={filters.merchant_id}
                  onChange={(e) =>
                    setFilters({ ...filters, merchant_id: e.target.value })
                  }
                >
                  <option value="">All</option>
                  {merchantOptions.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Status
                <select
                  value={filters.status}
                  onChange={(e) =>
                    setFilters({ ...filters, status: e.target.value })
                  }
                >
                  <option value="">All</option>
                  {STATUS_ORDER.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>External Ref</th>
                  <th>Shipment ID</th>
                </tr>
              </thead>
              <tbody>
                {shipments.length === 0 ? (
                  <tr>
                    <td colSpan={4}>
                      <div className="empty-state centered">
                        <h3>No shipments yet</h3>
                        <p>
                          Create a shipment to see idempotency, status
                          transitions, and event tracking in action.
                        </p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  shipments.map((shipment) => (
                    <tr
                      key={shipment.id}
                      onClick={() => loadShipmentDetail(shipment.id)}
                    >
                      <td>{shipment.name}</td>
                      <td>{shipment.status}</td>
                      <td>{shipment.external_reference}</td>
                      <td className="muted">{shipment.id}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </section>
        )}

        {view === "create" && (
          <section className="panel">
            <h2>Create Shipment</h2>
            <form className="form" onSubmit={handleCreateShipment}>
              <label>
                Merchant ID
                <select
                  value={createForm.merchant_id}
                  onChange={(e) =>
                    setCreateForm({ ...createForm, merchant_id: e.target.value })
                  }
                  required
                  disabled={merchantOptions.length === 0}
                >
                  <option value="">Select a merchant</option>
                  {merchantOptions.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name} ({m.id.slice(0, 8)})
                    </option>
                  ))}
                </select>
              </label>
              {merchantOptions.length === 0 && (
                <p className="error">Create a merchant before creating shipments.</p>
              )}
              <label>
                Name
                <input
                  value={createForm.name}
                  onChange={(e) =>
                    setCreateForm({ ...createForm, name: e.target.value })
                  }
                  required
                  disabled={merchantOptions.length === 0}
                />
                <span className="hint">
                  Human-readable label (e.g. Order #12345)
                </span>
              </label>
              <label>
                External Reference
                <input
                  value={createForm.external_reference}
                  onChange={(e) =>
                    setCreateForm({
                      ...createForm,
                      external_reference: e.target.value,
                    })
                  }
                  required
                  disabled={merchantOptions.length === 0}
                  placeholder="order-12345"
                />
                <span className="hint">
                  Used for idempotency. Submitting the same value twice returns
                  the same shipment. Example: order-12345
                </span>
              </label>
              <button type="submit">Create</button>
            </form>
            {createResult && (
              <div className="result">
                {createResult.error ? (
                  <p className="error">{createResult.error}</p>
                ) : (
                  <>
                    <p>
                      ✅ Shipment {createResult.created ? "created" : "reused"}
                    </p>
                    <p className="muted">Shipment ID: {createResult.id}</p>
                    <p className="muted">
                      Created: {createResult.created ? "true" : "false"}
                    </p>
                  </>
                )}
              </div>
            )}
          </section>
        )}

        {view === "detail" && selectedShipment && (
          <section className="panel">
            <div className="panel-header">
              <h2>Shipment Detail</h2>
              <button onClick={() => setView("shipments")}>
                Back to list
              </button>
            </div>
            <div className="detail-grid">
              <div>
                <h3>Metadata</h3>
                <p>
                  <strong>Name:</strong> {selectedShipment.name}
                </p>
                <p>
                  <strong>Status:</strong> {selectedShipment.status}
                </p>
                <p>
                  <strong>External Ref:</strong>{" "}
                  {selectedShipment.external_reference}
                </p>
                <p className="muted">{selectedShipment.id}</p>
              </div>
              <div>
                <h3>Status Transitions</h3>
                <p className="muted">Allowed transitions</p>
                <div className="status-actions">
                  {(STATUS_TRANSITIONS[selectedShipment.status] || []).map(
                    (status) => (
                      <button
                        key={status}
                        onClick={() => handleStatusChange(status)}
                      >
                        {status}
                      </button>
                    ),
                  )}
                </div>
                {statusUpdate && statusUpdate.ok && (
                  <p className="muted">Updated to {statusUpdate.status}</p>
                )}
                {statusUpdate && !statusUpdate.ok && (
                  <p className="error">{statusUpdate.message}</p>
                )}
              </div>
            </div>

            <div className="panel" id="event-timeline">
              <h3>Event Timeline</h3>
              <ul className="timeline">
                {events.map((event) => (
                  <li
                    key={event.id}
                    className={event.id === lastEventId ? "highlight" : ""}
                  >
                    <strong>{event.type}</strong>
                    <span>{new Date(event.occurred_at).toLocaleString()}</span>
                    {event.reason && <span>{event.reason}</span>}
                  </li>
                ))}
              </ul>
              <form className="form" onSubmit={handleAddEvent}>
                <div className="form-row">
                  <label>
                    Type
                    <select
                      value={eventForm.type}
                      onChange={(e) =>
                        setEventForm({ ...eventForm, type: e.target.value })
                      }
                    >
                      {EVENT_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Source
                    <select
                      value={eventForm.source}
                      onChange={(e) =>
                        setEventForm({ ...eventForm, source: e.target.value })
                      }
                    >
                      <option value="carrier">carrier</option>
                      <option value="system">system</option>
                      <option value="manual">manual</option>
                    </select>
                  </label>
                </div>
                <label>
                  Occurred At (optional, ISO)
                  <input
                    value={eventForm.occurred_at}
                    onChange={(e) =>
                      setEventForm({ ...eventForm, occurred_at: e.target.value })
                    }
                    placeholder="2024-01-01T12:00:00Z"
                  />
                </label>
                <label>
                  Reason (optional)
                  <input
                    value={eventForm.reason}
                    onChange={(e) =>
                      setEventForm({ ...eventForm, reason: e.target.value })
                    }
                  />
                </label>
                <button type="submit">Add Event</button>
              </form>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
