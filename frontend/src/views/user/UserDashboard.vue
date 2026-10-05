<!-- UserDashboard.vue — Trekker main dashboard to view their bookings -->
<script setup>
import { ref, computed, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const bookings  = ref([]);
const loading   = ref(true);
const exporting = ref(false);

const userName = computed(() => store.user?.full_name || store.user?.username || 'Trekker');

async function loadBookings() {
  loading.value = true;
  try {
    bookings.value = await api.getUserBookings();
  } catch (e) { store.notify(e.message, 'error'); }
  loading.value = false;
}

async function cancelBooking(b) {
  if (!confirm(`Cancel your booking for ${b.trek_name}?`)) return;
  try {
    await api.cancelBooking(b.id);
    store.notify('Booking cancelled');
    await loadBookings();
  } catch (e) { store.notify(e.message, 'error'); }
}

async function exportCSV() {
  exporting.value = true;
  try {
    const res = await api.exportCSV();
    store.notify("CSV export task started! Checking status...", "info");

    const taskId = res.task_id;
    const interval = setInterval(async () => {
      try {
        const statusRes = await api.getExportStatus(taskId);

        if (statusRes.status === "success") {
          clearInterval(interval);
          const filename = statusRes.result.filename;

          // Download CSV
          const blob = await api.downloadCSV(filename);
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");

          link.href = url;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          link.remove();
          window.URL.revokeObjectURL(url);
          store.notify("CSV downloaded successfully!", "success");
          exporting.value = false;
        } else if (statusRes.status === "failed") {
          clearInterval(interval);
          store.notify("CSV export failed", "error");
          exporting.value = false;
        }
      } catch (e) {
        clearInterval(interval);
        store.notify(e.message || "CSV download failed", "error");
        exporting.value = false;
      }
    }, 2000);
  } catch (e) {
    store.notify(e.message, "error");
    exporting.value = false;
  }
}

onMounted(loadBookings);
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="page-title mb-1">My Dashboard</h2>
        <p class="text-muted mb-0" style="font-size: 0.9rem;">Welcome back, {{ userName }}!</p>
      </div>
      <div class="d-flex gap-2">
        <router-link to="/user/explore" class="btn btn-sp-primary">Explore Treks</router-link>
        <button class="btn btn-sp-ghost" @click="exportCSV" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
          <span v-else class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle;">download</span>
          Export CSV
        </button>
      </div>
    </div>

    <div class="sp-card">
      <div class="sp-card-body p-0">
        <div class="p-3 border-bottom"><h5 class="font-heading mb-0" style="color: var(--sp-primary);">My Treks</h5></div>
        <div v-if="loading" class="sp-loading"><div class="spinner-border" style="color: var(--sp-primary);"></div></div>
        <div v-else-if="bookings.length === 0" class="text-center py-5 text-muted">
          <span class="material-symbols-outlined d-block mb-2" style="font-size: 48px;">hiking</span>
          You haven't booked any treks yet.
          <br><router-link to="/user/explore" class="btn btn-sp-primary mt-3">Find a Trek</router-link>
        </div>
        <div v-else class="table-responsive">
          <table class="table sp-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Trek</th>
                <th>Dates</th>
                <th>Booking Date</th>
                <th>Status</th>
                <th class="pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td class="ps-4" data-label="Trek">
                  <div style="font-weight: 600; color: var(--sp-primary);">{{ b.trek_name }}</div>
                  <div style="font-size: 0.75rem; color: var(--sp-muted);">{{ b.trek_location }}</div>
                </td>
                <td data-label="Dates"><span style="font-size: 0.875rem;">{{ b.start_date || 'TBD' }} to {{ b.end_date || 'TBD' }}</span></td>
                <td data-label="Booking Date"><span style="font-size: 0.875rem;">{{ new Date(b.booking_date).toLocaleDateString() }}</span></td>
                <td data-label="Status">
                  <span class="badge-status" :class="'badge-' + b.status.toLowerCase()">{{ b.status }}</span>
                </td>
                <td class="pe-4 actions-cell" data-label="Actions">
                  <button v-if="b.status === 'Booked'" class="btn btn-sm px-2" style="border: 1px solid #ffdad6; color: #ba1a1a; border-radius: 8px;" @click="cancelBooking(b)" title="Cancel Booking">
                    Cancel
                  </button>
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