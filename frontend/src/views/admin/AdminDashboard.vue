<!-- AdminDashboard.vue — KPI cards + ChartJS bookings chart + recent activity -->
<script setup>
import { ref, computed, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const loading   = ref(true);
const stats     = ref({});
const report    = ref(null);
const chartData = ref({ labels: [], data: [] });
let chartInstance = null;

/* ── Computed ─────────────────────────────────────────────────────────────── */
const kpis = computed(() => [
  {
    label: 'Total Treks',
    value: stats.value.total_treks    || 0,
    icon: 'landscape',
    iconBg: '#D8E2DC',
    iconColor: '#012d1d',
    sub: `${stats.value.open_treks || 0} open now`,
  },
  {
    label: 'Active Users',
    value: stats.value.total_users    || 0,
    icon: 'group',
    iconBg: '#c1ecd4',
    iconColor: '#012d1d',
    sub: 'registered trekkers',
  },
  {
    label: 'Trek Staff',
    value: stats.value.total_staff    || 0,
    icon: 'directions_walk',
    iconBg: '#FFE5D9',
    iconColor: '#924c00',
    sub: 'on-field guides',
  },
  {
    label: 'Total Bookings',
    value: stats.value.total_bookings || 0,
    icon: 'book_online',
    iconBg: '#ffdcc4',
    iconColor: '#6f3800',
    sub: `${stats.value.active_bookings || 0} active`,
  },
]);

const statusSummary = computed(() => {
  if (!stats.value.trek_statuses) return [];
  return stats.value.trek_statuses;
});

/* ── Methods ──────────────────────────────────────────────────────────────── */
async function loadStats() {
  try {
    stats.value = await api.getAdminStats();
  } catch {}
}

async function loadChart() {
  try {
    chartData.value = await api.getChartData();
    renderChart();
  } catch {}
}

async function loadReport() {
  try {
    report.value = await api.getMonthlyReport();
    store.notify('Monthly report loaded!', 'success');
  } catch (e) {
    store.notify(e.message, 'error');
  }
}

function renderChart() {
  const canvas = document.getElementById('adminChart');
  if (!canvas) return;
  if (chartInstance) chartInstance.destroy();

  const ctx  = canvas.getContext('2d');
  const grad = ctx.createLinearGradient(0, 0, 0, 250);
  grad.addColorStop(0, 'rgba(1,45,29,.15)');
  grad.addColorStop(1, 'rgba(1,45,29,0)');

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.value.labels || ['No Data'],
      datasets: [
        {
          label: 'Bookings',
          data: chartData.value.data || [0],
          backgroundColor:
            chartData.value.labels?.map((_, i) =>
              i === 0 ? '#012d1d' : 'rgba(1,45,29,.35)'
            ) || ['rgba(1,45,29,.35)'],
          borderRadius: 6,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#191c1d',
          titleFont: { family: 'Geist', size: 12, weight: 'bold' },
          bodyFont:  { family: 'Inter', size: 13 },
          padding: 10,
          cornerRadius: 8,
          displayColors: false,
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Geist', size: 11 }, color: '#6C757D' },
        },
        y: {
          grid: { color: '#E9ECEF', drawBorder: false },
          ticks: { font: { family: 'Geist', size: 11 }, color: '#6C757D' },
          beginAtZero: true,
        },
      },
    },
  });
}

/* ── Lifecycle ────────────────────────────────────────────────────────────── */
onMounted(async () => {
  loading.value = true;
  await Promise.all([loadStats(), loadChart()]);
  loading.value = false;
});
</script>

<template>
  <div>
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h2 class="page-title mb-1">Overview</h2>
        <p class="text-muted mb-0" style="font-size: 0.9rem;">
          Real-time metrics for your trekking operations.
        </p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-sp-ghost btn-sm" @click="loadReport">
          <span class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle;">
            description
          </span>
          Monthly Report
        </button>
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3" v-for="kpi in kpis" :key="kpi.label">
        <div class="kpi-card">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <span class="section-label">{{ kpi.label }}</span>
            <div class="kpi-icon" :style="{ background: kpi.iconBg }">
              <span
                class="material-symbols-outlined"
                :style="{ color: kpi.iconColor, fontSize: '20px' }"
              >{{ kpi.icon }}</span>
            </div>
          </div>
          <div class="kpi-number">{{ loading ? '—' : kpi.value }}</div>
          <div class="mt-1" style="font-size: 0.75rem; color: #6c757d;">{{ kpi.sub }}</div>
        </div>
      </div>
    </div>

    <!-- Bento: Chart + Quick Actions -->
    <div class="row g-3 mb-4">
      <!-- Chart -->
      <div class="col-lg-8">
        <div class="sp-card h-100">
          <div class="sp-card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="font-heading mb-0" style="color: var(--sp-primary);">
                Popular Treks (Bookings)
              </h5>
              <span class="section-label">YTD</span>
            </div>
            <div style="position: relative; height: 250px;">
              <canvas id="adminChart"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="col-lg-4">
        <div class="sp-card h-100">
          <div class="sp-card-body">
            <h5 class="font-heading mb-3" style="color: var(--sp-primary);">Quick Actions</h5>
            <div class="d-grid gap-2">
              <router-link to="/admin/treks" class="btn btn-sp-primary d-flex align-items-center gap-2">
                <span class="material-symbols-outlined" style="font-size: 18px;">add_circle</span>
                Add New Trek
              </router-link>
              <router-link to="/admin/staff" class="btn btn-sp-ghost d-flex align-items-center gap-2">
                <span class="material-symbols-outlined" style="font-size: 18px;">person_add</span>
                Add Staff Member
              </router-link>
              <router-link to="/admin/bookings" class="btn btn-sp-ghost d-flex align-items-center gap-2">
                <span class="material-symbols-outlined" style="font-size: 18px;">book_online</span>
                View All Bookings
              </router-link>
              <router-link to="/admin/users" class="btn btn-sp-ghost d-flex align-items-center gap-2">
                <span class="material-symbols-outlined" style="font-size: 18px;">manage_accounts</span>
                Manage Users
              </router-link>
            </div>

            <!-- Monthly Report Preview -->
            <div
              v-if="report"
              class="mt-4 p-3 rounded"
              style="background: #f8f9fa; border: 1px solid var(--sp-border);"
            >
              <div class="section-label mb-2">{{ report.month }} Summary</div>
              <div class="d-flex justify-content-between py-1">
                <span style="font-size: 0.85rem;">Treks Created</span>
                <strong>{{ report.total_treks }}</strong>
              </div>
              <div class="d-flex justify-content-between py-1">
                <span style="font-size: 0.85rem;">Bookings</span>
                <strong>{{ report.total_bookings }}</strong>
              </div>
              <div class="d-flex justify-content-between py-1">
                <span style="font-size: 0.85rem;">Participants</span>
                <strong>{{ report.total_participants }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Trek Status Overview -->
    <div class="row g-3">
      <div class="col-12">
        <div class="sp-card">
          <div class="sp-card-body">
            <h5 class="font-heading mb-3" style="color: var(--sp-primary);">Trek Status Overview</h5>
            <div class="d-flex flex-wrap gap-3">
              <div
                v-for="s in statusSummary"
                :key="s.label"
                class="d-flex align-items-center gap-2 p-2 rounded"
                style="background: #f8f9fa;"
              >
                <span class="badge-status" :class="'badge-' + s.label.toLowerCase()">
                  {{ s.label }}
                </span>
                <strong style="font-family: Geist, sans-serif;">{{ s.count }}</strong>
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