<!-- AppLayout.vue — Main application layout with Sidebar and Topbar -->
<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import store from '@/store';

const router = useRouter();

const roleDisplay = computed(() => {
  if (store.isAdmin) return 'Admin Portal';
  if (store.isStaff) return 'Staff Portal';
  return 'Trekker Portal';
});

const navLinks = computed(() => {
  if (store.isAdmin) {
    return [
      { path: '/admin/dashboard', label: 'Overview',        icon: 'dashboard' },
      { path: '/admin/treks',     label: 'Trek Management', icon: 'landscape' },
      { path: '/admin/bookings',  label: 'Bookings',        icon: 'book_online' },
      { path: '/admin/staff',     label: 'Staff Directory', icon: 'directions_walk' },
      { path: '/admin/users',     label: 'User Directory',  icon: 'group' },
    ];
  }
  if (store.isStaff) {
    return [
      { path: '/staff/dashboard', label: 'Dashboard', icon: 'dashboard' },
    ];
  }
  if (store.isUser) {
    return [
      { path: '/user/dashboard', label: 'My Dashboard',    icon: 'dashboard' },
      { path: '/user/explore',   label: 'Explore Treks',   icon: 'travel_explore' },
      { path: '/user/profile',   label: 'Profile Settings', icon: 'manage_accounts' },
    ];
  }
  return [];
});

function doLogout() {
  store.logout();
  router.push('/login');
}
</script>

<template>
  <div class="d-flex">
    <!-- Toast Container -->
    <div class="sp-toast-wrap">
      <transition-group name="fade">
        <div
          v-for="n in store.notifications"
          :key="n.id"
          class="sp-toast"
          :class="'sp-toast-' + n.type"
        >
          <span class="material-symbols-outlined" style="font-size: 20px;">
            {{ n.type === 'success' ? 'check_circle' : (n.type === 'error' ? 'error' : 'info') }}
          </span>
          <div style="flex-grow: 1;">{{ n.message }}</div>
        </div>
      </transition-group>
    </div>

    <!-- Mobile Overlay -->
    <div
      v-if="store.sidebarOpen"
      class="sp-overlay d-md-none"
      @click="store.sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside class="sp-sidebar" :class="{ open: store.sidebarOpen }">
      <div class="d-flex align-items-center gap-2 mb-4 px-2">
        <div class="sp-sidebar-logo">
          <span class="material-symbols-outlined">landscape</span>
        </div>
        <div>
          <h6 class="font-heading mb-0" style="color: var(--sp-primary);">Trekify</h6>
          <div style="font-size: 0.7rem; color: var(--sp-muted); letter-spacing: 0.05em; text-transform: uppercase;">
            {{ roleDisplay }}
          </div>
        </div>
      </div>

      <!-- Navigation links dynamically generated based on role -->
      <nav class="d-flex flex-column gap-1 flex-grow-1">
        <router-link
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          class="sp-nav-link"
          active-class="active"
          @click="store.sidebarOpen = false"
        >
          <span class="material-symbols-outlined">{{ link.icon }}</span>
          {{ link.label }}
        </router-link>
      </nav>
    </aside>

    <!-- Main Content Area -->
    <div class="sp-main flex-grow-1">
      <!-- Topbar -->
      <header class="d-flex justify-content-between align-items-center mb-4">
        <div class="d-flex align-items-center gap-3">
          <button
            class="btn d-md-none p-0"
            style="color: var(--sp-primary);"
            @click="store.sidebarOpen = !store.sidebarOpen"
          >
            <span class="material-symbols-outlined">menu</span>
          </button>
        </div>

        <div class="dropdown">
          <div class="d-flex align-items-center gap-2 cursor-pointer" data-bs-toggle="dropdown">
            <div class="text-end d-none d-sm-block">
              <div style="font-size: 0.85rem; font-weight: 600; color: var(--sp-primary);">
                {{ store.user?.full_name || store.user?.username }}
              </div>
              <div style="font-size: 0.75rem; color: var(--sp-muted);">{{ store.user?.email }}</div>
            </div>
            <div class="avatar shadow-sm border" style="background: #fff;">{{ store.userInitials }}</div>
          </div>
          <ul
            class="dropdown-menu dropdown-menu-end shadow-sm"
            style="border-radius: var(--sp-radius-sm); border: 1px solid var(--sp-border); font-size: 0.875rem;"
          >
            <li v-if="store.isUser">
              <router-link class="dropdown-item py-2" to="/user/profile">My Profile</router-link>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item py-2 text-danger cursor-pointer" @click="doLogout">Sign Out</a>
            </li>
          </ul>
        </div>
      </header>

      <!-- Page Content -->
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<style scoped>
</style>