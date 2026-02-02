const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  let response;
  try {
    const mergedHeaders = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };
    const { headers: _ignored, ...restOptions } = options;
    response = await fetch(`${API_BASE}${path}`, {
      headers: mergedHeaders,
      ...restOptions,
    });
  } catch (error) {
    return {
      ok: false,
      status: 0,
      body: null,
      networkError: error instanceof Error ? error.message : "Network error",
    };
  }

  const text = await response.text();
  let body = null;
  let parseError = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch (error) {
      parseError = error instanceof Error ? error.message : "Response parse error";
    }
  }
  return { ok: response.ok, status: response.status, body, parseError };
}

export const api = {
  getMerchants() {
    return request("/merchant");
  },
  createMerchant(payload) {
    return request("/merchant", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  getShipments(params) {
    const query = new URLSearchParams(params || {}).toString();
    const suffix = query ? `?${query}` : "";
    return request(`/shipments${suffix}`);
  },
  getShipment(id) {
    return request(`/shipments/${id}`);
  },
  createShipment(payload) {
    return request("/shipments", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  updateShipmentStatus(id, status) {
    return request(`/shipments/${id}/status`, {
      method: "POST",
      body: JSON.stringify({ status }),
    });
  },
  listEvents(id) {
    return request(`/shipments/${id}/events`);
  },
  addEvent(id, payload) {
    return request(`/shipments/${id}/events`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
