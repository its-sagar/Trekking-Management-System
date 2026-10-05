/* router/index.js — Vue Router 4 setup with role-based guards */
import { createRouter, createWebHistory } from 'vue-router';
import store from '@/store';
import api   from '@/api';

import LoginPage          from '@/views/LoginPage.vue';
import AppLayout          from '@/layouts/AppLayout.vue';
import AdminDashboard     from '@/views/admin/AdminDashboard.vue';
import TrekManagement     from '@/views/admin/TrekManagement.vue';
import StaffManagement    from '@/views/admin/StaffManagement.vue';
import UserManagement     from '@/views/admin/UserManagement.vue';
import BookingsManagement from '@/views/admin/BookingsManagement.vue';
import StaffDashboard     from '@/views/staff/StaffDashboard.vue';
import UserDashboard      from '@/views/user/UserDashboard.vue';
import ExploreTreks       from '@/views/user/ExploreTreks.vue';
import UserProfile        from '@/views/user/UserProfile.vue';

/* ── Routes ──────────────────────────────────────────────────────────────── */
const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginPage },
  {
    path: '/',
    component: AppLayout,
    children: [
      /* Admin Routes */
      { path: 'admin/dashboard', component: AdminDashboard,     meta: { role: 'admin' } },
      { path: 'admin/treks',     component: TrekManagement,     meta: { role: 'admin' } },
      { path: 'admin/staff',     component: StaffManagement,    meta: { role: 'admin' } },
      { path: 'admin/users',     component: UserManagement,     meta: { role: 'admin' } },
      { path: 'admin/bookings',  component: BookingsManagement, meta: { role: 'admin' } },

      /* Staff Routes */
      { path: 'staff/dashboard', component: StaffDashboard, meta: { role: 'staff' } },

      /* User Routes */
      { path: 'user/dashboard',  component: UserDashboard, meta: { role: 'user' } },
      { path: 'user/explore',    component: ExploreTreks,  meta: { role: 'user' } },
      { path: 'user/profile',    component: UserProfile,   meta: { role: 'user' } },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

/* ── Navigation Guards ───────────────────────────────────────────────────── */
router.beforeEach(async (to, from, next) => {
  // If we have a token but no user object, try to fetch it
  if (store.token && !store.user) {
    try {
      store.user = await api.getMe();
    } catch {
      store.logout();
      if (to.path !== '/login') return next('/login');
    }
  }

  const isAuthPage = to.path === '/login';
  const isLoggedIn = !!store.token;

  if (isAuthPage && isLoggedIn) {
    if (store.isAdmin) return next('/admin/dashboard');
    if (store.isStaff) return next('/staff/dashboard');
    return next('/user/dashboard');
  }

  if (!isAuthPage && !isLoggedIn) {
    return next('/login');
  }

  // Role-based route protection
  if (to.meta.role && store.user?.role !== to.meta.role) {
    store.notify('Unauthorized access', 'error');
    if (store.isAdmin) return next('/admin/dashboard');
    if (store.isStaff) return next('/staff/dashboard');
    return next('/user/dashboard');
  }

  next();
});

export default router;