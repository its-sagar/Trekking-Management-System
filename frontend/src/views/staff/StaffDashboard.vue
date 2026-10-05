<!-- StaffDashboard.vue — Staff main dashboard to view assigned treks -->
<script setup>
import { ref, reactive, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const stats               = ref({});
const treks               = ref([]);
const loading             = ref(true);
const saving              = ref(false);
const showModal           = ref(false);
const activeTrek          = reactive({});
const participants        = ref([]);
const loadingParticipants = ref(false);

async function loadDashboard() {
  loading.value = true;
  try {
    stats.value = await api.getStaffStats();
    treks.value = await api.getStaffTreks();
  } catch (e) { store.notify(e.message, 'error'); }
  loading.value = false;
}

async function openManage(trek) {
  Object.assign(activeTrek, { id: trek.id, name: trek.name, available_slots: trek.available_slots, status: trek.status });
  showModal.value = true;
  loadingParticipants.value = true;
  try {
    participants.value = await api.getParticipants(trek.id);
  } catch (e) { store.notify('Could not load participants', 'error'); }
  loadingParticipants.value = false;
}

async function saveTrek() {
  saving.value = true;
  try {
    await api.updateStaffTrek(activeTrek.id, { available_slots: activeTrek.available_slots, status: activeTrek.status });
    store.notify('Trek updated');
    showModal.value = false;
    await loadDashboard();
  } catch (e) { store.notify(e.message, 'error'); }
  saving.value = false;
}

onMounted(loadDashboard);
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="page-title mb-1">Staff Dashboard</h2>
        <p class="text-muted mb-0" style="font-size: 0.9rem;">Manage your assigned treks and participants.</p>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="kpi-card">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <span class="section-label">Assigned Treks</span>
            <div class="kpi-icon" style="background: #D8E2DC;"><span class="material-symbols-outlined" style="color: #012d1d;">landscape</span></div>
          </div>
          <div class="kpi-number">{{ stats.assigned_treks || 0 }}</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="kpi-card">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <span class="section-label">Total Participants</span>
            <div class="kpi-icon" style="background: #c1ecd4;"><span class="material-symbols-outlined" style="color: #012d1d;">group</span></div>
          </div>
          <div class="kpi-number">{{ stats.total_participants || 0 }}</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="kpi-card">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <span class="section-label">Open Treks</span>
            <div class="kpi-icon" style="background: #FFE5D9;"><span class="material-symbols-outlined" style="color: #924c00;">hiking</span></div>
          </div>
          <div class="kpi-number">{{ stats.open_treks || 0 }}</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="kpi-card">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <span class="section-label">Completed</span>
            <div class="kpi-icon" style="background: #e9ecef;"><span class="material-symbols-outlined" style="color: #495057;">check_circle</span></div>
          </div>
          <div class="kpi-number">{{ stats.completed_treks || 0 }}</div>
        </div>
      </div>
    </div>

    <div class="sp-card">
      <div class="sp-card-body p-0">
        <div class="p-3 border-bottom"><h5 class="font-heading mb-0" style="color: var(--sp-primary);">My Treks</h5></div>
        <div v-if="loading" class="sp-loading"><div class="spinner-border" style="color: var(--sp-primary);"></div></div>
        <div v-else-if="treks.length === 0" class="text-center py-5 text-muted">You have no assigned treks.</div>
        <div v-else class="table-responsive">
          <table class="table sp-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Trek</th>
                <th>Dates</th>
                <th>Status</th>
                <th>Slots (Available/Total)</th>
                <th>Participants</th>
                <th class="pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trek in treks" :key="trek.id">
                <td class="ps-4" data-label="Trek"><span style="font-weight: 600; color: var(--sp-primary);">{{ trek.name }}</span></td>
                <td data-label="Dates"><span style="font-size: 0.875rem;">{{ trek.start_date || 'TBD' }} to {{ trek.end_date || 'TBD' }}</span></td>
                <td data-label="Status"><span class="badge-status" :class="'badge-' + trek.status.toLowerCase()">{{ trek.status }}</span></td>
                <td data-label="Slots (Available/Total)"><span style="font-size: 0.875rem;">{{ trek.available_slots }} / {{ trek.total_slots }}</span></td>
                <td data-label="Participants"><span style="font-size: 0.875rem; font-weight: 600;">{{ trek.participant_count }}</span></td>
                <td class="pe-4 actions-cell" data-label="Actions">
                  <button class="btn btn-sm btn-sp-ghost px-2" @click="openManage(trek)" title="Manage">
                    <span class="material-symbols-outlined" style="font-size: 16px;">settings</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Manage Trek Modal -->
    <div v-if="showModal" class="sp-overlay" @click.self="showModal = false"></div>
    <div v-if="showModal" class="modal d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content" style="border-radius: var(--sp-radius);">
          <div class="modal-header" style="border-bottom: 1px solid var(--sp-border);">
            <h5 class="modal-title font-heading" style="color: var(--sp-primary);">Manage: {{ activeTrek.name }}</h5>
            <button class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-4">
              <div class="col-md-5">
                <h6 class="font-heading" style="color: var(--sp-primary);">Update Details</h6>
                <div class="mb-3">
                  <label class="form-label">Available Slots</label>
                  <input type="number" v-model.number="activeTrek.available_slots" class="form-control" min="0">
                </div>
                <div class="mb-3">
                  <label class="form-label">Status</label>
                  <select v-model="activeTrek.status" class="form-select">
                    <option>Open</option>
                    <option>Closed</option>
                    <option>Completed</option>
                  </select>
                </div>
                <button class="btn btn-sp-primary w-100" @click="saveTrek" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span> Update
                </button>
              </div>
              <div class="col-md-7 border-start">
                <h6 class="font-heading" style="color: var(--sp-primary);">Participants</h6>
                <div v-if="loadingParticipants" class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary-sp"></div></div>
                <div v-else-if="participants.length === 0" class="text-muted" style="font-size: 0.875rem;">No participants yet.</div>
                <ul v-else class="list-group list-group-flush" style="max-height: 300px; overflow-y: auto;">
                  <li v-for="p in participants" :key="p.id" class="list-group-item d-flex justify-content-between align-items-center" style="font-size: 0.875rem;">
                    <div>
                      <strong>{{ p.user_name }}</strong><br>
                      <span class="text-muted" style="font-size: 0.75rem;">{{ p.user_email }}</span>
                    </div>
                    <span class="badge-status" :class="'badge-' + p.status.toLowerCase()">{{ p.status }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>