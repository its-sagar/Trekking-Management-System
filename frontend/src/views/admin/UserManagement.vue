<!-- UserManagement.vue — Admin view to manage Users -->
<script setup>
import { ref, reactive, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const users   = ref([]);
const loading = ref(true);
const filters = reactive({ q: '' });

let debounceTimer = null;
function debouncedSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadUsers, 350);
}

async function loadUsers() {
  loading.value = true;
  try {
    users.value = await api.getAdminUsers(filters.q);
  } catch (e) { store.notify(e.message, 'error'); }
  loading.value = false;
}

async function toggleActive(user) {
  try {
    await api.updateUserStatus(user.id, { is_active: !user.is_active });
    store.notify(`User ${user.is_active ? 'deactivated' : 'activated'}`);
    await loadUsers();
  } catch (e) { store.notify(e.message, 'error'); }
}

async function toggleBlacklist(user) {
  if (!confirm(`Are you sure you want to ${user.is_blacklisted ? 'remove blacklist from' : 'blacklist'} this user?`)) return;
  try {
    await api.updateUserStatus(user.id, { is_blacklisted: !user.is_blacklisted });
    store.notify(`User ${user.is_blacklisted ? 'un-blacklisted' : 'blacklisted'}`);
    await loadUsers();
  } catch (e) { store.notify(e.message, 'error'); }
}

onMounted(loadUsers);
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="page-title mb-1">User Directory</h2>
        <p class="text-muted mb-0" style="font-size: 0.9rem;">Manage registered trekkers.</p>
      </div>
    </div>

    <div class="sp-card mb-4">
      <div class="sp-card-body">
        <div class="row g-3">
          <div class="col-md-6">
            <input v-model="filters.q" @input="debouncedSearch" class="form-control" placeholder="Search by name, email, or username...">
          </div>
        </div>
      </div>
    </div>

    <div class="sp-card">
      <div class="sp-card-body p-0">
        <div v-if="loading" class="sp-loading"><div class="spinner-border" style="color: var(--sp-primary);"></div></div>
        <div v-else-if="users.length === 0" class="text-center py-5 text-muted">No users found.</div>
        <div v-else class="table-responsive">
          <table class="table sp-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">User</th>
                <th>Contact</th>
                <th>Joined</th>
                <th>Status</th>
                <th class="pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td class="ps-4" data-label="User">
                  <div style="font-weight: 600; color: var(--sp-primary);">{{ user.full_name || user.username }}</div>
                  <div style="font-size: 0.75rem; color: var(--sp-muted);">@{{ user.username }}</div>
                </td>
                <td data-label="Contact">
                  <div style="font-size: 0.875rem;">{{ user.email }}</div>
                  <div style="font-size: 0.75rem; color: var(--sp-muted);">{{ user.phone || '—' }}</div>
                </td>
                <td data-label="Joined"><span style="font-size: 0.875rem;">{{ new Date(user.created_at).toLocaleDateString() }}</span></td>
                <td data-label="Status">
                  <span class="badge-status" :class="user.is_blacklisted ? 'badge-closed' : (user.is_active ? 'badge-open' : 'badge-pending')">
                    {{ user.is_blacklisted ? 'Blacklisted' : (user.is_active ? 'Active' : 'Deactivated') }}
                  </span>
                </td>
                <td class="pe-4 actions-cell" data-label="Actions">
                  <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-sp-ghost px-2" @click="toggleActive(user)" :title="user.is_active ? 'Deactivate' : 'Activate'">
                      <span class="material-symbols-outlined" style="font-size: 16px;">{{ user.is_active ? 'block' : 'check_circle' }}</span>
                    </button>
                    <button
                      class="btn btn-sm px-2"
                      :style="user.is_blacklisted ? 'border:1px solid #1b4332;color:#1b4332;border-radius:8px;' : 'border:1px solid #ffdad6;color:#ba1a1a;border-radius:8px;'"
                      @click="toggleBlacklist(user)"
                      :title="user.is_blacklisted ? 'Remove Blacklist' : 'Blacklist'"
                    >
                      <span class="material-symbols-outlined" style="font-size: 16px;">gavel</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>