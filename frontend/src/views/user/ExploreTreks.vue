<!-- ExploreTreks.vue — User view to search and book treks -->
<script setup>
import { ref, reactive, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const treks        = ref([]);
const loading      = ref(true);
const showModal    = ref(false);
const booking      = ref(false);
const selectedTrek = ref(null);
const bookingNotes = ref('');
const filters      = reactive({ q: '', difficulty: '', duration: '' });

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
    if (filters.duration)   params.set('duration',    filters.duration);
    treks.value = await api.searchTreks(params.toString());
  } catch (e) { store.notify(e.message, 'error'); }
  loading.value = false;
}

function openBook(trek) {
  selectedTrek.value = trek;
  bookingNotes.value = '';
  showModal.value = true;
}

async function doBook() {
  booking.value = true;
  try {
    await api.bookTrek(selectedTrek.value.id, { notes: bookingNotes.value });
    store.notify('Booking successful!', 'success');
    showModal.value = false;
    await loadTreks(); // refresh slots
  } catch (e) { store.notify(e.message, 'error'); }
  booking.value = false;
}

onMounted(loadTreks);
</script>

<template>
  <div>
    <div class="mb-4 text-center py-5 rounded" style="background: linear-gradient(135deg, #012d1d, #1b4332); color: white; position: relative; overflow: hidden;">
      <div style="position: absolute; top: -50%; left: -10%; width: 120%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);"></div>
      <h2 class="font-heading" style="font-size: 2.5rem; z-index: 1; position: relative;">Find Your Next Adventure</h2>
      <p style="font-size: 1.1rem; opacity: 0.9; z-index: 1; position: relative;">Explore the world's most breathtaking trails.</p>
    </div>

    <div class="sp-card mb-4" style="margin-top: -50px; position: relative; z-index: 2; margin-left: 5%; margin-right: 5%;">
      <div class="sp-card-body p-3">
        <div class="row g-2 align-items-end">
          <div class="col-md-4">
            <label class="form-label mb-1">Search</label>
            <input v-model="filters.q" @input="debouncedSearch" class="form-control" placeholder="Trek name or location...">
          </div>
          <div class="col-md-3">
            <label class="form-label mb-1">Difficulty</label>
            <select v-model="filters.difficulty" @change="loadTreks" class="form-select">
              <option value="">Any</option><option>Easy</option><option>Moderate</option><option>Hard</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label mb-1">Max Duration (Days)</label>
            <input type="number" v-model.number="filters.duration" @input="debouncedSearch" class="form-control" placeholder="e.g. 7">
          </div>
          <div class="col-md-2">
            <button class="btn btn-sp-primary w-100 h-100 py-2" @click="loadTreks">Search</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="sp-loading"><div class="spinner-border" style="color: var(--sp-primary);"></div></div>
    <div v-else-if="treks.length === 0" class="text-center py-5 text-muted">No treks found matching your criteria.</div>
    <div v-else class="row g-4">
      <div class="col-md-6 col-lg-4" v-for="trek in treks" :key="trek.id">
        <div class="sp-card h-100 d-flex flex-column" style="overflow: hidden;">
          <div class="trek-card-header">
            <span v-if="trek.image_url"><img :src="trek.image_url" class="trek-card-img"></span>
            <span v-else class="material-symbols-outlined" style="font-size: 48px; color: rgba(255,255,255,0.2);">landscape</span>
            <span class="badge-status trek-card-difficulty" :class="'badge-' + trek.difficulty.toLowerCase()">{{ trek.difficulty }}</span>
          </div>
          <div class="sp-card-body flex-grow-1 d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="font-heading mb-0" style="color: var(--sp-primary); font-size: 1.1rem;">{{ trek.name }}</h5>
              <span style="font-family: Geist, sans-serif; font-weight: 700; color: var(--sp-secondary);">₹{{ trek.price }}</span>
            </div>
            <div class="d-flex align-items-center gap-1 mb-3" style="color: var(--sp-muted); font-size: 0.8rem;">
              <span class="material-symbols-outlined" style="font-size: 14px;">location_on</span> {{ trek.location }}
            </div>
            <p class="mb-3" style="font-size: 0.875rem; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">{{ trek.description }}</p>

            <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
              <div style="font-size: 0.8rem;">
                <div class="d-flex align-items-center gap-1"><span class="material-symbols-outlined" style="font-size: 14px;">calendar_month</span> {{ trek.duration_days }} Days</div>
                <div class="d-flex align-items-center gap-1 mt-1"><span class="material-symbols-outlined" style="font-size: 14px;">group</span> {{ trek.available_slots }} slots left</div>
              </div>
              <button class="btn btn-sp-cta px-4" @click="openBook(trek)" :disabled="trek.available_slots <= 0">Book</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Book Modal -->
    <div v-if="showModal" class="sp-overlay" @click.self="showModal = false"></div>
    <div v-if="showModal" class="modal d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content" style="border-radius: var(--sp-radius);">
          <div class="modal-header" style="border-bottom: 1px solid var(--sp-border);">
            <h5 class="modal-title font-heading" style="color: var(--sp-primary);">Book Trek</h5>
            <button class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <h6 class="font-heading" style="color: var(--sp-primary);">{{ selectedTrek.name }}</h6>
            <p class="text-muted" style="font-size: 0.875rem;">Dates: {{ selectedTrek.start_date }} to {{ selectedTrek.end_date }}</p>
            <div class="mb-3 mt-3">
              <label class="form-label">Notes / Requirements</label>
              <textarea v-model="bookingNotes" class="form-control" rows="3" placeholder="Dietary requirements, medical info..."></textarea>
            </div>
            <div class="d-flex justify-content-between align-items-center p-3 rounded" style="background: #f8f9fa;">
              <span class="font-heading" style="font-size: 1.1rem; color: var(--sp-primary);">Total to pay:</span>
              <span class="font-heading" style="font-size: 1.25rem; color: var(--sp-secondary);">₹{{ selectedTrek.price }}</span>
            </div>
          </div>
          <div class="modal-footer" style="border-top: 1px solid var(--sp-border);">
            <button class="btn btn-sp-ghost" @click="showModal = false">Cancel</button>
            <button class="btn btn-sp-cta" @click="doBook" :disabled="booking">
              <span v-if="booking" class="spinner-border spinner-border-sm me-1"></span> Confirm Booking
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
