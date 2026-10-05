<!-- UserProfile.vue — User view to manage their profile -->
<script setup>
import { ref, reactive, onMounted } from 'vue';
import api   from '@/api';
import store from '@/store';

const profile = ref({});
const form    = reactive({ full_name: '', phone: '', password: '' });
const loading = ref(true);
const saving  = ref(false);

async function loadProfile() {
  loading.value = true;
  try {
    const p = await api.getProfile();
    profile.value = p;
    form.full_name = p.full_name || '';
    form.phone     = p.phone     || '';
  } catch (e) { store.notify('Could not load profile', 'error'); }
  loading.value = false;
}

async function saveProfile() {
  saving.value = true;
  try {
    const p = await api.updateProfile(form);
    profile.value = p;
    form.password = '';
    store.user.full_name = p.full_name; // Update store to reflect in navbar
    store.notify('Profile updated successfully!', 'success');
  } catch (e) { store.notify(e.message, 'error'); }
  saving.value = false;
}

onMounted(loadProfile);
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="page-title mb-1">My Profile</h2>
          <p class="text-muted mb-0" style="font-size: 0.9rem;">Manage your personal information.</p>
        </div>
      </div>

      <div class="sp-card">
        <div class="sp-card-body p-4">
          <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary-sp"></div></div>
          <form v-else @submit.prevent="saveProfile">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input :value="profile.username" class="form-control" disabled style="background: #f8f9fa;">
            </div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input :value="profile.email" class="form-control" disabled style="background: #f8f9fa;">
            </div>
            <div class="mb-3">
              <label class="form-label">Full Name</label>
              <input v-model="form.full_name" class="form-control" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Phone Number</label>
              <input v-model="form.phone" class="form-control">
            </div>

            <hr class="my-4">
            <h6 class="font-heading mb-3" style="color: var(--sp-primary);">Change Password</h6>
            <div class="mb-3">
              <label class="form-label">New Password (leave blank to keep current)</label>
              <input type="password" v-model="form.password" class="form-control" minlength="6">
            </div>

            <div class="d-flex justify-content-end mt-4 pt-3 border-top">
              <button type="submit" class="btn btn-sp-primary px-4" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span> Save Profile
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
