/* store/index.js — Reactive global state using Vue 3 reactivity */
import { reactive } from 'vue';

const store = reactive({
  user: null,
  token: localStorage.getItem('token') || null,
  notifications: [],
  sidebarOpen: false,

  /* ── Auth ─────────────────────────────────────────────────────────────── */
  setAuth(token, user) {
    this.token = token;
    this.user  = user;
    localStorage.setItem('token', token);
  },
  logout() {
    this.token = null;
    this.user  = null;
    localStorage.removeItem('token');
  },

  /* ── Notifications ────────────────────────────────────────────────────── */
  notify(message, type = 'success') {
    const id = Date.now() + Math.random();
    this.notifications.push({ id, message, type });
    setTimeout(() => {
      const idx = this.notifications.findIndex(n => n.id === id);
      if (idx > -1) this.notifications.splice(idx, 1);
    }, 4000);
  },

  /* ── Computed-like helpers ────────────────────────────────────────────── */
  get isLoggedIn() { return !!this.token; },
  get isAdmin()    { return this.user?.role === 'admin'; },
  get isStaff()    { return this.user?.role === 'staff'; },
  get isUser()     { return this.user?.role === 'user'; },

  get userInitials() {
    const name = this.user?.full_name || this.user?.username || '?';
    return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
  },
});

export default store;