<!-- LoginPage.vue — Login + Register forms with tab toggle -->
<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import api   from '@/api';
import store from '@/store';

const router = useRouter();

const tab      = ref('login');
const showPwd  = ref(false);
const loading  = ref(false);
const error    = ref('');
const canRegister = true; // only users can register; admin/staff login only

const loginForm = reactive({ email: '', password: '' });
const regForm   = reactive({
  first_name: '',
  last_name:  '',
  username:   '',
  email:      '',
  phone:      '',
  password:   '',
});

async function doLogin() {
  error.value   = '';
  loading.value = true;
  try {
    const res  = await api.login(loginForm.email, loginForm.password);
    store.setAuth(res.token, res.user);
    const role = res.user.role;
    if      (role === 'admin') router.push('/admin/dashboard');
    else if (role === 'staff') router.push('/staff/dashboard');
    else                       router.push('/user/dashboard');
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function doRegister() {
  error.value   = '';
  loading.value = true;
  try {
    const res = await api.register({
      username:  regForm.username,
      email:     regForm.email,
      password:  regForm.password,
      full_name: `${regForm.first_name} ${regForm.last_name}`.trim(),
      phone:     regForm.phone,
    });
    store.setAuth(res.token, res.user);
    router.push('/user/dashboard');
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div
    class="min-vh-100 d-flex align-items-center justify-content-center"
    style="background: linear-gradient(135deg, #012d1d 0%, #1b4332 50%, #2d6a4f 100%);"
  >
    <div class="container" style="max-width: 460px;">
      <!-- Logo -->
      <div class="text-center mb-4">
        <div class="d-inline-flex align-items-center gap-3 mb-3">
          <div
            class="rounded-circle d-flex align-items-center justify-content-center"
            style="width: 56px; height: 56px; background: rgba(255,255,255,.15);"
          >
            <span class="material-symbols-outlined text-white" style="font-size: 32px;">landscape</span>
          </div>
          <div class="text-start">
            <h1
              class="text-white mb-0"
              style="font-family: Geist, sans-serif; font-size: 1.75rem; font-weight: 700;"
            >Trekify</h1>
            <p
              class="mb-0"
              style="color: rgba(255,255,255,.7); font-size: 0.8rem; letter-spacing: .08em; text-transform: uppercase; font-family: Geist, sans-serif;"
            >Trekking Management Platform</p>
          </div>
        </div>
      </div>

      <!-- Card -->
      <div class="sp-card">
        <div class="sp-card-body p-4">
          <!-- Tab Switcher -->
          <div class="d-flex rounded mb-4" style="background: #f3f4f5; padding: 4px;">
            <button
              class="flex-fill btn rounded py-2"
              :class="tab === 'login' ? 'btn-sp-primary' : 'bg-transparent text-muted'"
              @click="tab = 'login'"
            >
              Sign In
            </button>
            <button
              v-if="canRegister"
              class="flex-fill btn rounded py-2"
              :class="tab === 'register' ? 'btn-sp-primary' : 'bg-transparent text-muted'"
              @click="tab = 'register'"
            >
              Create Account
            </button>
          </div>

          <!-- Login Form -->
          <form v-if="tab === 'login'" @submit.prevent="doLogin">
            <div class="mb-3">
              <label class="form-label">Email Address</label>
              <input
                v-model="loginForm.email"
                type="email"
                class="form-control"
                placeholder="you@example.com"
                required
                autocomplete="email"
              >
            </div>
            <div class="mb-4">
              <label class="form-label">Password</label>
              <div class="position-relative">
                <input
                  v-model="loginForm.password"
                  :type="showPwd ? 'text' : 'password'"
                  class="form-control"
                  placeholder="••••••••"
                  required
                  autocomplete="current-password"
                >
                <button
                  type="button"
                  class="btn btn-sm position-absolute top-50 end-0 translate-middle-y me-1"
                  style="background: none; border: none;"
                  @click="showPwd = !showPwd"
                >
                  <span class="material-symbols-outlined" style="font-size: 18px; color: #6c757d;">
                    {{ showPwd ? 'visibility_off' : 'visibility' }}
                  </span>
                </button>
              </div>
            </div>
            <div v-if="error" class="alert alert-danger py-2 mb-3" style="font-size: 0.875rem;">{{ error }}</div>
            <button type="submit" class="btn btn-sp-primary w-100 py-2" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Sign In
            </button>
          </form>

          <!-- Register Form -->
          <form v-if="tab === 'register'" @submit.prevent="doRegister">
            <div class="row g-3 mb-3">
              <div class="col-6">
                <label class="form-label">First Name</label>
                <input v-model="regForm.first_name" type="text" class="form-control" placeholder="Arjun" required>
              </div>
              <div class="col-6">
                <label class="form-label">Last Name</label>
                <input v-model="regForm.last_name" type="text" class="form-control" placeholder="Mehta">
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input v-model="regForm.username" type="text" class="form-control" placeholder="trekker_arjun" required minlength="3">
            </div>
            <div class="mb-3">
              <label class="form-label">Email Address</label>
              <input v-model="regForm.email" type="email" class="form-control" placeholder="arjun@example.com" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Phone</label>
              <input v-model="regForm.phone" type="tel" class="form-control" placeholder="+91-9876543210">
            </div>
            <div class="mb-4">
              <label class="form-label">Password</label>
              <input v-model="regForm.password" type="password" class="form-control" placeholder="Min. 6 characters" required minlength="6">
            </div>
            <div v-if="error" class="alert alert-danger py-2 mb-3" style="font-size: 0.875rem;">{{ error }}</div>
            <button type="submit" class="btn btn-sp-primary w-100 py-2" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Create Account
            </button>
          </form>
        </div>
      </div>
      <p class="text-center mt-3" style="color: rgba(255,255,255,.5); font-size: 0.8rem;">
        © 2025 Trekify · All rights reserved
      </p>
    </div>
  </div>
</template>

<style scoped>
</style>