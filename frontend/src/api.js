const isLocalHost =
  window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";

const API_BASE = isLocalHost ? "http://127.0.0.1:8000/api" : "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Falha na comunicacao com a API.");
  }

  return response.json();
}

export const api = {
  login: (payload) =>
    request("/login", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  users: () => request("/users"),
  createUser: (payload) =>
    request("/users", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  userSettings: (userId) => request(`/users/${userId}/settings`),
  updateUserSettings: (userId, payload) =>
    request(`/users/${userId}/settings`, {
      method: "PUT",
      body: JSON.stringify(payload)
    }),
  deleteUser: (userId) =>
    request(`/users/${userId}`, {
      method: "DELETE"
    }),
  categories: () => request("/categories"),
  createCategory: (payload) =>
    request("/categories", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  transactions: (userId, month) =>
    request(`/transactions?user_id=${userId}${month ? `&month=${month}` : ""}`),
  createTransaction: (payload) =>
    request("/transactions", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  deleteTransaction: (transactionId) =>
    request(`/transactions/${transactionId}`, {
      method: "DELETE"
    }),
  services: (userId, month) =>
    request(`/services?user_id=${userId}${month ? `&month=${month}` : ""}`),
  servicesSummary: (userId, month) =>
    request(`/services/summary?user_id=${userId}${month ? `&month=${month}` : ""}`),
  createService: (payload) =>
    request("/services", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  updateService: (serviceId, payload) =>
    request(`/services/${serviceId}`, {
      method: "PUT",
      body: JSON.stringify(payload)
    }),
  deleteService: (serviceId) =>
    request(`/services/${serviceId}`, {
      method: "DELETE"
    }),
  dashboard: (userId, month) =>
    request(`/dashboard?user_id=${userId}${month ? `&month=${month}` : ""}`),
  reports: (userId, month) =>
    request(`/reports?user_id=${userId}${month ? `&month=${month}` : ""}`),
  exportInfo: () => request("/export-info"),
  exportUrl: (format, userId, month) =>
    `${API_BASE}/exports/${format}?user_id=${userId}${month ? `&month=${month}` : ""}`
};
