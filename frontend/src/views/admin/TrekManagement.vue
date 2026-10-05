<!-- TrekManagement.vue — Full CRUD for treks (Admin) -->
<script setup>
import { ref, reactive, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const treks          = ref([]);
const allStaff       = ref([]);
const loading        = ref(true);
const saving         = ref(false);
const showModal      = ref(false);
const showAssign     = ref(false);
const formError      = ref('');
const assignTrek     = ref(null);
const selectedStaffId = ref(null);

const filters  = reactive({ q: '', difficulty: '', status: '' });
const editTrek = reactive({
  id: null, name: '', location: '', difficulty: 'Moderate',
  duration_days: 7, total_slots: 20, available_slots: 20,
  status: 'Pending', start_date: '', end_date: '',
  description: '', price: 0, image_url: '',
});

let debounceTimer = null;
function debouncedSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadTreks, 350);
}

async function loadTreks() {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (filters.q)          params.set('q',          filters.q);
    if (filters.difficulty) params.set('difficulty',  filters.difficulty);
    if (filters.status)     params.set('status',      filters.status);
    treks.value = await api.getAdminTreks(params.toString());
  } catch (e) { store.notify(e.message, 'error'); }
  loading.value = false;
}

function clearFilters() {
  filters.q = ''; filters.difficulty = ''; filters.status = '';
  loadTreks();
}

function openModal(trek = null) {
  formError.value = '';
  if (trek) {
    Object.assign(editTrek, { ...trek });
  } else {
    Object.assign(editTrek, {
      id: null, name: '', location: '', difficulty: 'Moderate',
      duration_days: 7, total_slots: 20, available_slots: 20,
      status: 'Pending', start_date: '', end_date: '',
      description: '', price: 0, image_url: '',
    });
  }
  showModal.value = true;
}

async function saveTrek() {
  if (!editTrek.name.trim()) { formError.value = 'Trek name is required'; return; }
  saving.value = true; formError.value = '';
  try {
    if (editTrek.id) {
      await api.updateTrek(editTrek.id, { ...editTrek });
      store.notify('Trek updated!');
    } else {
      await api.createTrek({ ...editTrek });
      store.notify('Trek created!');
    }
    showModal.value = false;
    await loadTreks();
  } catch (e) { formError.value = e.message; }
  saving.value = false;
}

async function confirmDelete(trek) {
  if (!confirm(`Delete "${trek.name}"? This cannot be undone.`)) return;
  try {
    await api.deleteTrek(trek.id);
    store.notify('Trek deleted');
    await loadTreks();
  } catch (e) { store.notify(e.message, 'error'); }
}

async function openAssign(trek) {
  assignTrek.value = trek;
  selectedStaffId.value = trek.assigned_staff_id || null;
  if (!allStaff.value.length) {
    allStaff.value = await api.getAdminStaff();
  }
  showAssign.value = true;
}

async function doAssign() {
  saving.value = true;
  try {
    await api.assignStaff(assignTrek.value.id, selectedStaffId.value);
    store.notify('Staff assigned!');
    showAssign.value = false;
    await loadTreks();
  } catch (e) { store.notify(e.message, 'error'); }
  saving.value = false;
}

function slotPct(trek) {
  if (!trek.total_slots) return 0;
  return Math.round((trek.available_slots / trek.total_slots) * 100);
}

onMounted(loadTreks);
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="page-title mb-1">Trek Management</h2>
        <p class="text-muted mb-0" style="font-size: 0.9rem;">Create, update, and assign treks to staff.</p>
      </div>
      <button class="btn btn-sp-primary d-flex align-items-center gap-2" @click="openModal()">
        <span class="material-symbols-outlined" style="font-size: 18px;">add</span> New Trek
      </button>
    </div>

    <!-- Filters -->
    <div class="sp-card mb-4">
      <div class="sp-card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <input v-model="filters.q" @input="debouncedSearch" class="form-control" placeholder="Search by name or location…">
          </div>
          <div class="col-md-3">
            <select v-model="filters.difficulty" @change="loadTreks" class="form-select">
              <option value="">All Difficulties</option>
              <option>Easy</option><option>Moderate</option><option>Hard</option>
            </select>
          </div>
          <div class="col-md-3">
            <select v-model="filters.status" @change="loadTreks" class="form-select">
              <option value="">All Statuses</option>
              <option>Pending</option><option>Approved</option><option>Open</option><option>Closed</option><option>Completed</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-sp-ghost w-100" @click="clearFilters">Clear</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="sp-card">
      <div class="sp-card-body p-0">
        <div v-if="loading" class="sp-loading"><div class="spinner-border" style="color: var(--sp-primary);"></div></div>
        <div v-else-if="treks.length === 0" class="text-center py-5 text-muted">
          <span class="material-symbols-outlined d-block mb-2" style="font-size: 48px;">landscape</span>
          No treks found. Create your first one!
        </div>
        <div v-else class="table-responsive">
          <table class="table sp-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Trek</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Duration</th>
                <th>Slots</th>
                <th>Staff</th>
                <th>Status</th>
                <th>Price</th>
                <th class="pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trek in treks" :key="trek.id">
                <td class="ps-4" data-label="Trek">
                  <div style="font-weight: 600; font-family: Geist, sans-serif; color: var(--sp-primary);">{{ trek.name }}</div>
                  <div style="font-size: 0.75rem; color: var(--sp-muted);">{{ trek.start_date || 'TBD' }} → {{ trek.end_date || 'TBD' }}</div>
                </td>
                <td data-label="Location">
                  <div class="d-flex align-items-center gap-1">
                    <span class="material-symbols-outlined" style="font-size: 14px; color: var(--sp-muted);">location_on</span>
                    <span style="font-size: 0.875rem;">{{ trek.location || '—' }}</span>
                  </div>
                </td>
                <td data-label="Difficulty"><span class="badge-status" :class="'badge-' + trek.difficulty.toLowerCase()">{{ trek.difficulty }}</span></td>
                <td data-label="Duration"><span style="font-size: 0.875rem;">{{ trek.duration_days }}d</span></td>
                <td data-label="Slots">
                  <span style="font-size: 0.875rem;">{{ trek.available_slots }}/{{ trek.total_slots }}</span>
                  <div class="progress mt-1" style="height: 4px; border-radius: 9999px;">
                    <div class="progress-bar" :style="{ width: slotPct(trek) + '%', background: 'var(--sp-primary)' }"></div>
                  </div>
                </td>
                <td data-label="Staff"><span style="font-size: 0.875rem;">{{ trek.assigned_staff_name || '—' }}</span></td>
                <td data-label="Status"><span class="badge-status" :class="'badge-' + trek.status.toLowerCase()">{{ trek.status }}</span></td>
                <td data-label="Price"><span style="font-size: 0.875rem; font-family: Geist, sans-serif;">₹{{ trek.price?.toLocaleString() || 0 }}</span></td>
                <td class="pe-4 actions-cell" data-label="Actions">
                  <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-sp-ghost px-2" @click="openAssign(trek)" title="Assign Staff">
                      <span class="material-symbols-outlined" style="font-size: 16px;">person_add</span>
                    </button>
                    <button class="btn btn-sm btn-sp-ghost px-2" @click="openModal(trek)" title="Edit">
                      <span class="material-symbols-outlined" style="font-size: 16px;">edit</span>
                    </button>
                    <button class="btn btn-sm px-2" style="border: 1px solid #ffdad6; color: #ba1a1a; border-radius: 8px;" @click="confirmDelete(trek)" title="Delete">
                      <span class="material-symbols-outlined" style="font-size: 16px;">delete</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Trek Modal -->
    <div v-if="showModal" class="sp-overlay" @click.self="showModal = false"></div>
    <div v-if="showModal" class="modal d-block" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content" style="border-radius: var(--sp-radius); border: 1px solid var(--sp-border);">
          <div class="modal-header" style="border-bottom: 1px solid var(--sp-border);">
            <h5 class="modal-title font-heading" style="color: var(--sp-primary);">{{ editTrek.id ? 'Edit Trek' : 'Create New Trek' }}</h5>
            <button class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <form id="trekForm" @submit.prevent="saveTrek">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">Trek Name *</label>
                  <input v-model="editTrek.name" class="form-control" required placeholder="e.g. Everest Base Camp Trek">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Location</label>
                  <input v-model="editTrek.location" class="form-control" placeholder="e.g. Nepal">
                </div>
                <div class="col-md-3">
                  <label class="form-label">Difficulty</label>
                  <select v-model="editTrek.difficulty" class="form-select">
                    <option>Easy</option><option>Moderate</option><option>Hard</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Duration (days)</label>
                  <input v-model.number="editTrek.duration_days" type="number" min="1" class="form-control">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Start Date</label>
                  <input v-model="editTrek.start_date" type="date" class="form-control">
                </div>
                <div class="col-md-4">
                  <label class="form-label">End Date</label>
                  <input v-model="editTrek.end_date" type="date" class="form-control">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Total Slots</label>
                  <input v-model.number="editTrek.total_slots" type="number" min="1" class="form-control">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Price (₹)</label>
                  <input v-model.number="editTrek.price" type="number" min="0" class="form-control">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Status</label>
                  <select v-model="editTrek.status" class="form-select">
                    <option>Pending</option><option>Approved</option><option>Open</option><option>Closed</option><option>Completed</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Available Slots</label>
                  <input v-model.number="editTrek.available_slots" type="number" min="0" class="form-control">
                </div>
                <div class="col-md-12">
                  <label class="form-label">Image URL</label>
                  <input v-model="editTrek.image_url" class="form-control" placeholder="https://example.com/image.jpg">
                </div>
                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea v-model="editTrek.description" class="form-control" rows="3" placeholder="Trek description…"></textarea>
                </div>
              </div>
            </form>
            <div v-if="formError" class="alert alert-danger mt-3 py-2" style="font-size: 0.875rem;">{{ formError }}</div>
          </div>
          <div class="modal-footer" style="border-top: 1px solid var(--sp-border);">
            <button class="btn btn-sp-ghost" @click="showModal = false">Cancel</button>
            <button class="btn btn-sp-primary" @click="saveTrek" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ editTrek.id ? 'Save Changes' : 'Create Trek' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign Staff Modal -->
    <div v-if="showAssign" class="sp-overlay" @click.self="showAssign = false"></div>
    <div v-if="showAssign" class="modal d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered" style="max-width: 400px;">
        <div class="modal-content" style="border-radius: var(--sp-radius);">
          <div class="modal-header" style="border-bottom: 1px solid var(--sp-border);">
            <h5 class="modal-title font-heading" style="color: var(--sp-primary);">Assign Staff</h5>
            <button class="btn-close" @click="showAssign = false"></button>
          </div>
          <div class="modal-body">
            <p style="font-size: 0.875rem; color: var(--sp-muted);">Trek: <strong style="color: var(--sp-primary);">{{ assignTrek?.name }}</strong></p>
            <label class="form-label">Select Staff Member</label>
            <select v-model="selectedStaffId" class="form-select">
              <option :value="null">— Unassign —</option>
              <option v-for="s in allStaff" :key="s.id" :value="s.id">{{ s.full_name || s.username }} ({{ s.email }})</option>
            </select>
          </div>
          <div class="modal-footer" style="border-top: 1px solid var(--sp-border);">
            <button class="btn btn-sp-ghost" @click="showAssign = false">Cancel</button>
            <button class="btn btn-sp-primary" @click="doAssign" :disabled="saving">Assign</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>