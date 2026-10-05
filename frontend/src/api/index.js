/* api/index.js — Centralized fetch wrapper with JWT injection */
const API_BASE = "/api";

const api = {
  _getHeaders() {
    const token = localStorage.getItem("token");
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  },

  async _request(method, path, body = null) {
    const opts = { method, headers: this._getHeaders() };
    if (body !== null) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${path}`, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
  },

  async _download(path) {
    const token = localStorage.getItem("token");

    const res = await fetch(`${API_BASE}${path}`, {
      method: "GET",
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return await res.blob();
  },

  get: (path) => api._request("GET", path),
  post: (path, body) => api._request("POST", path, body),
  put: (path, body) => api._request("PUT", path, body),
  delete: (path) => api._request("DELETE", path),

  /* ── Auth ─────────────────────────────────────────────────────────────── */
  login: (email, password) => api.post("/auth/login", { email, password }),
  register: (data) => api.post("/auth/register", data),
  getMe: () => api.get("/auth/me"),

  /* ── Admin ────────────────────────────────────────────────────────────── */
  getAdminStats: () => api.get("/admin/stats"),
  getAdminTreks: (qs = "") => api.get(`/admin/treks${qs ? "?" + qs : ""}`),
  createTrek: (d) => api.post("/admin/treks", d),
  updateTrek: (id, d) => api.put(`/admin/treks/${id}`, d),
  deleteTrek: (id) => api.delete(`/admin/treks/${id}`),
  assignStaff: (tid, sid) =>
    api.post(`/admin/treks/${tid}/assign-staff`, { staff_id: sid }),
  getAdminStaff: (q = "") => api.get(`/admin/staff${q ? "?q=" + q : ""}`),
  createStaff: (d) => api.post("/admin/staff", d),
  updateStaff: (id, d) => api.put(`/admin/staff/${id}`, d),
  getAdminUsers: (q = "") => api.get(`/admin/users${q ? "?q=" + q : ""}`),
  updateUserStatus: (id, d) => api.put(`/admin/users/${id}/status`, d),
  getAdminBookings: () => api.get("/admin/bookings"),
  getChartData: () => api.get("/admin/chart/bookings"),
  getMonthlyReport: () => api.get("/admin/reports/monthly"),

  /* ── Staff ────────────────────────────────────────────────────────────── */
  getStaffStats: () => api.get("/staff/stats"),
  getStaffTreks: () => api.get("/staff/treks"),
  updateStaffTrek: (id, d) => api.put(`/staff/treks/${id}`, d),
  getParticipants: (id) => api.get(`/staff/treks/${id}/participants`),

  /* ── User ─────────────────────────────────────────────────────────────── */
  getOpenTreks: () => api.get("/user/treks"),
  searchTreks: (qs) => api.get(`/user/treks/search?${qs}`),
  getTrekDetail: (id) => api.get(`/user/treks/${id}`),
  bookTrek: (id, d) => api.post(`/user/treks/${id}/book`, d),
  getUserBookings: () => api.get("/user/bookings"),
  cancelBooking: (id) => api.delete(`/user/bookings/${id}`),
  getProfile: () => api.get("/user/profile"),
  updateProfile: (d) => api.put("/user/profile", d),
  exportCSV: () => api.post("/user/export-csv", {}),
  getExportStatus: (tid) => api.get(`/user/export-status/${tid}`),
  downloadCSV: (filename) => api._download(`/user/download-csv/${encodeURIComponent(filename)}`),
};

export default api;
