<!-- BookingsManagement.vue — Admin view to see all bookings -->
<script setup>
import { ref, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const bookings = ref([]);
const loading  = ref(true);

async function loadBookings() {
  loading.value = true;
  try {
    bookings.value = await api.getAdminBookings();
  } catch (e) {
    store.notify(e.message, 'error');
  }
  loading.value = false;
}

onMounted(loadBookings);
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="page-title mb-1">Bookings Overview</h2>
        <p class="text-muted mb-0" style="font-size: 0.9rem;">View all trekking reservations.</p>
      </div>
    </div>

    <div class="sp-card">
      <div class="sp-card-body p-0">
        <div v-if="loading" class="sp-loading">
          <div class="spinner-border" style="color: var(--sp-primary);"></div>
        </div>
        <div v-else-if="bookings.length === 0" class="text-center py-5 text-muted">
          No bookings found.
        </div>
        <div v-else class="table-responsive">
          <table class="table sp-table mb-0">
            <thead>
              <tr>
                <th class="ps-4">Booking ID</th>
                <th>Trekker</th>
                <th>Trek Details</th>
                <th>Dates</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td class="ps-4" data-label="Booking ID">
                  <span style="font-family: Geist, sans-serif; font-weight: 600; color: var(--sp-primary);">
                    #BKG-{{ b.id.toString().padStart(4, '0') }}
                  </span>
                </td>
                <td data-label="Trekker">
                  <div style="font-weight: 600; color: var(--sp-primary);">{{ b.user_name }}</div>
                  <div style="font-size: 0.75rem; color: var(--sp-muted);">{{ b.user_email }}</div>
                </td>
                <td data-label="Trek Details">
                  <div style="font-weight: 600; color: var(--sp-primary);">{{ b.trek_name }}</div>
                  <div style="font-size: 0.75rem; color: var(--sp-muted);">{{ b.trek_location }}</div>
                </td>
                <td data-label="Dates"><span style="font-size: 0.875rem;">{{ b.start_date || 'TBD' }}</span></td>
                <td data-label="Status">
                  <span class="badge-status" :class="'badge-' + b.status.toLowerCase()">
                    {{ b.status }}
                  </span>
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