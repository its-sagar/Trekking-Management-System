<!-- StaffManagement.vue — Admin view to manage Staff -->
<script setup>
import { ref, reactive, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const staffList  = ref([]);
const loading    = ref(true);
const saving     = ref(false);
const showModal  = ref(false);
const formError  = ref('');
const filters    = reactive({ q: '' });
const editStaff  = reactive({
  id: null, full_name: '', username: '', email: '',
  password: '', phone: '', is_active: true, is_blacklisted: false,
});

let debounceTimer = null;
function debouncedSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadStaff, 350);
}

async function loadStaff() {
  loading.value = true;
  try {
    staffList.value = await api.getAdminStaff(filters.q);
  } catch (e) { store.notify(e.message, 'error'); }
  loading.value = false;
}

function openModal(staff = null) {
  formError.value = '';
  if (staff) {
    Object.assign(editStaff, { ...staff, password: '' });
  } else {
    Object.assign(editStaff, { id: null, full_name: '', username: '', email: '', password: '', phone: '', is_active: true, is_blacklisted: false });
  }
  showModal.value = true;
}

async function saveStaff() {
  saving.value = true; formError.value = '';
  try {
    if (editStaff.id) {
      await api.updateStaff(editStaff.id, editStaff);
      store.notify('Staff updated!');
    } else {
      await api.createStaff(editStaff);
      store.notify('Staff created!');
    }
    showModal.value = false;
    await loadStaff();
  } catch (e) { formError.value = e.message; }
  saving.value = false;
}

onMounted(loadStaff);
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="page-title mb-1">Staff Directory</h2>
        <p class="text-muted mb-0" style="font-size: 0.9rem;">Manage trekking guides and field staff.</p>
      </div>
      <button class="btn btn-sp-primary d-flex align-items-center gap-2" @click="openModal()">
        <span class="material-symbols-outlined" style="font-size: 18px;">person_add</span> Add Staff
      </button>
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
        <div v-else-if="staffList.length === 0" class="text-center py-5 text-muted">No staff members found.</div>
        <div v-else class="table-responsive">
          <table class="table sp-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Name</th>
                <th>Contact</th>
                <th>Username</th>
                <th>Status</th>
                <th>Joined</th>
                <th class="pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="staff in staffList" :key="staff.id">
                <td class="ps-4" data-label="Name">
                  <div class="d-flex align-items-center gap-3">
                    <div class="avatar">{{ staff.full_name?.charAt(0) || staff.username.charAt(0) }}</div>
                    <div style="font-weight: 600; color: var(--sp-primary);">{{ staff.full_name || '—' }}</div>
                  </div>
                </td>
                <td data-label="Contact">
                  <div style="font-size: 0.875rem;">{{ staff.email }}</div>
                  <div style="font-size: 0.75rem; color: var(--sp-muted);">{{ staff.phone || 'No phone' }}</div>
                </td>
                <td data-label="Username"><span style="font-size: 0.875rem;">{{ staff.username }}</span></td>
                <td data-label="Status">
                  <span class="badge-status" :class="staff.is_active && !staff.is_blacklisted ? 'badge-open' : 'badge-closed'">
                    {{ staff.is_blacklisted ? 'Blacklisted' : (staff.is_active ? 'Active' : 'Inactive') }}
                  </span>
                </td>
                <td data-label="Joined"><span style="font-size: 0.875rem;">{{ new Date(staff.created_at).toLocaleDateString() }}</span></td>
                <td class="pe-4 actions-cell" data-label="Actions">
                  <button class="btn btn-sm btn-sp-ghost px-2" @click="openModal(staff)" title="Edit">
                    <span class="material-symbols-outlined" style="font-size: 16px;">edit</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Staff Modal -->
    <div v-if="showModal" class="sp-overlay" @click.self="showModal = false"></div>
    <div v-if="showModal" class="modal d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content" style="border-radius: var(--sp-radius);">
          <div class="modal-header" style="border-bottom: 1px solid var(--sp-border);">
            <h5 class="modal-title font-heading" style="color: var(--sp-primary);">{{ editStaff.id ? 'Edit Staff' : 'Add New Staff' }}</h5>
            <button class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveStaff">
              <div class="mb-3">
                <label class="form-label">Full Name *</label>
                <input v-model="editStaff.full_name" class="form-control" required>
              </div>
              <div class="mb-3" v-if="!editStaff.id">
                <label class="form-label">Username *</label>
                <input v-model="editStaff.username" class="form-control" required>
              </div>
              <div class="mb-3" v-if="!editStaff.id">
                <label class="form-label">Email *</label>
                <input v-model="editStaff.email" type="email" class="form-control" required>
              </div>
              <div class="mb-3" v-if="!editStaff.id">
                <label class="form-label">Password *</label>
                <input v-model="editStaff.password" type="password" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input v-model="editStaff.phone" class="form-control">
              </div>
              <div v-if="editStaff.id" class="form-check form-switch mb-2">
                <input class="form-check-input" type="checkbox" v-model="editStaff.is_active" id="activeCheck">
                <label class="form-check-label" for="activeCheck">Active Account</label>
              </div>
              <div v-if="editStaff.id" class="form-check form-switch">
                <input class="form-check-input" type="checkbox" v-model="editStaff.is_blacklisted" id="blacklistCheck">
                <label class="form-check-label text-danger" for="blacklistCheck">Blacklisted</label>
              </div>
            </form>
            <div v-if="formError" class="alert alert-danger mt-3 py-2" style="font-size: 0.875rem;">{{ formError }}</div>
          </div>
          <div class="modal-footer" style="border-top: 1px solid var(--sp-border);">
            <button class="btn btn-sp-ghost" @click="showModal = false">Cancel</button>
            <button class="btn btn-sp-primary" @click="saveStaff" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ editStaff.id ? 'Save Changes' : 'Add Staff' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>