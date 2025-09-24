<template>
  <div class="page-wrapper">
    <div ref="vantaBg" class="vanta-bg"></div>
    <div v-if="showRememberPopup" class="popup-overlay"></div>
    <div class="login-content">
      <div v-if="!showRememberPopup" class="login-container">
        <h2 class="login-headline">Login</h2>
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label>Username</label>
            <input v-model="username" type="text" class="form-control" required />
          </div>
          <div class="mb-3">
            <label>Password</label>
            <div class="password-icon-group">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="form-control"
                required
                ref="passwordInput"
              />
              <span class="icon-eye" @click.stop="toggleShowPassword" tabindex="0">
                <font-awesome-icon
                  v-if="!showPassword"
                  :icon="['fas', 'eye']"
                  style="color: #4fd1c5; margin-bottom: 1rem; font-size: 1.5rem; vertical-align: middle;" />
                <font-awesome-icon
                  v-else
                  :icon="['fas', 'eye-slash']"
                  style="color: #4fd1c5; margin-bottom: 1rem; font-size: 1.5rem; vertical-align: middle;" />
              </span>
            </div>
          </div>
          <div class="mb-3 form-check">
            <input v-model="rememberMe" type="checkbox" class="form-check-input" id="rememberMe" />
            <label class="form-check-label" for="rememberMe">Remember me</label>
          </div>
          <button class="nav-btn" type="submit">Login</button>
          <div v-if="error" class="error">{{ error }}</div>
        </form>
      </div>
      <div v-if="showRememberPopup" class="remember-popup">
        <p>Login as <b>{{ rememberedUsername }}</b>?</p>
        <button class="nav-btn" @click="loginAsRemembered">Yes, continue as {{ rememberedUsername }}</button>
        <button class="nav-btn alt" @click="showRememberPopup = false">Other user</button>
      </div>
    </div>
    <button class="back-btn" @click="goBack" @mouseenter="isHoveringBack = true" @mouseleave="isHoveringBack = false">
      <font-awesome-icon :icon="['fas', 'angles-left']" :fade="isHoveringBack" style="color: #ffffff; font-size: 2.2rem;" />
    </button>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'UserLogin',
  data() {
    return {
      username: '',
      password: '',
      rememberMe: false,
      showPassword: false,
      error: '',
      vantaEffect: null,
      isHoveringBack: false,
      showRememberPopup: false,
      rememberedUsername: ''
    }
  },
  mounted() {
    // Vanta background
    const tryInit = () => {
      if (window.VANTA && window.VANTA.TOPOLOGY) {
        this.vantaEffect = window.VANTA.TOPOLOGY({
          el: this.$refs.vantaBg,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 800.0,
          minWidth: 800.0,
          scale: 1.0,
          scaleMobile: 1.0,
          backgroundColor: 0x0f111a,
          color: 0x4fd1c5,
          spacing: 40,
          points: 12,
          maxDistance: 25
        });
      } else {
        setTimeout(tryInit, 100);
      }
    };
    tryInit();
    // Only call /api/user/dashboard to check for remembered user
    (async () => {
      try {
        const res = await axios.get('http://localhost:5000/api/user/dashboard', { withCredentials: true })
        if (res && res.data && res.data.username && res.data.is_remembered) {
          this.rememberedUsername = res.data.username
          this.showRememberPopup = true
        }
      } catch (e) {
        // Instead of error, log a custom message
        console.log('No remembered user found or not authenticated.');
      }
    })();
  },
  beforeUnmount() {
    if (this.vantaEffect) this.vantaEffect.destroy();
  },
  methods: {
    toggleShowPassword() {
      this.showPassword = !this.showPassword
    },
    async handleLogin() {
      this.error = ''
      try {
        const res = await axios.post('http://localhost:5000/api/auth/login', {
          username: this.username,
          password: this.password,
          remember: this.rememberMe
        }, { withCredentials: true })
        // After login, check dashboard type
        const dashRes = await axios.get('http://localhost:5000/api/user/dashboard', { withCredentials: true })
        if (dashRes.data && dashRes.data.dashboard_type === 'admin') {
          this.$router.push('/admin-dashboard')
        } else if (dashRes.data && dashRes.data.dashboard_type === 'user') {
          this.$router.push('/dashboard')
        } else {
          // fallback: go to /dashboard for non-teacher
          this.$router.push('/register')
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed'
      }
    },
    loginAsRemembered() {
      // Check dashboard type for remembered user
      axios.get('http://localhost:5000/api/user/dashboard', { withCredentials: true })
        .then(res => {
          if (res.data && res.data.dashboard_type === 'admin') {
            this.$router.push('/admin-dashboard')
          } else {
            this.$router.push('/dashboard')
          }
        })
    },
    goBack() {
      if (window.history.length > 1) {
        this.$router.back();
      } else {
        this.$router.push('/');
      }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css?family=Montserrat:400,700');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
@font-face {
  font-family: 'Megum';
  src: url('@/assets/fonts/Megum.otf') format('opentype');
  font-weight: normal;
  font-style: normal;
}
.page-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: #000;
}
.vanta-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
}
.login-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.login-container {
  width: 440px;
  min-width: 440px;
  max-width: 440px;
  height: 480px;
  margin: 2rem auto;
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  background: rgba(30, 30, 30, 0.15);
  border-radius: 16px;
  box-shadow: 0 0 24px 8px rgba(255,255,255,0.10);
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.login-headline {
  font-family: 'Megum', 'Montserrat', sans-serif;
  font-size: 3rem;
  font-weight: normal;
  color: #fff;
  margin-bottom: 2rem;
  text-align: center;
  letter-spacing: 0.08em;
  line-height: 1.1;
  background: none;
}
form {
  width: 100%;
}
label, .form-check-label {
  font-family: 'Orbitron', sans-serif;
  color: #d6e0df;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}
input, .form-control {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  color: #fff;
  background: rgba(30, 30, 30, 0.15);
  border-radius: 8px;
  border: 2px solid #ffffff64;
  margin-bottom: 1rem;
  padding: calc(0.5rem - 1px);
  transition: border-color 0.2s;
  box-sizing: border-box;
}
input:focus, .form-control:focus {
  outline: none;
  border-color: #4fd1c5;
}
.nav-btn {
  font-family: 'Orbitron', sans-serif;
  color: #fff;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  padding: 0.5rem 0;
  border-radius: 16px;
  background: rgba(30, 30, 30, 0.15);
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  border: none;
  box-shadow: 0 0 24px 8px rgba(255,255,255,0.10);
  transition: background 0.3s cubic-bezier(.4,2,.6,1), color 0.2s, box-shadow 0.3s cubic-bezier(.4,2,.6,1);
  cursor: pointer;
  outline: none;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-width: 180px;
  max-width: 100%;
  margin-top: 1.5rem;
}
.nav-btn:hover {
  background: rgba(79, 209, 197, 0.18);
  color: #4fd1c5;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.18) inset, 0 0 16px 4px rgba(79,209,197,0.10);
}
.password-icon-group {
  position: relative;
  display: flex;
  align-items: center;
}
.password-icon-group input {
  flex: 1;
  padding-right: 2.5rem;
}
.icon-eye {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 1.5rem;
  z-index: 10;
  color: #ffffff;
  display: flex;
  align-items: center;
  height: 100%;
  background: transparent;
  pointer-events: auto;
}
.icon-eye:active, .icon-eye:focus {
  outline: none;
}
.password-icon-group input:focus + .icon-eye svg {
  color: #4fd1c5;
}
.password-icon-group input:focus + .icon-eye,
.icon-eye:focus svg {
  color: #4fd1c5;
}
.error {
  color: #e74c3c;
  margin-top: 1rem;
  font-family: 'Orbitron', sans-serif;
}
input[type="checkbox"].form-check-input:checked {
  background-color: #4fd1c5;
  border-color: #4fd1c5;
}
input[type="checkbox"].form-check-input {
  accent-color: #4fd1c5;
  cursor: pointer;
  box-shadow: none;
  outline: none;
  border: 1.5px solid #4fd1c5;
  transition: border 0.2s, box-shadow 0.2s;
}
input[type="checkbox"].form-check-input:focus {
  outline: none;
  box-shadow: none;
  border: 1.5px solid #4fd1c5;
}
input[type="checkbox"].form-check-input:active {
  outline: none;
  box-shadow: none;
  border: 1.5px solid #4fd1c5;
}
.back-btn {
  position: fixed;
  top: 2.5rem;
  left: 2.5rem;
  z-index: 2000;
  background: rgba(30, 30, 30, 0.25);
  border: none;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px 0 rgba(31,38,135,0.18);
  cursor: pointer;
  transition: background 0.2s;
}
.back-btn:hover {
  background: rgba(79, 209, 197, 0.18);
}
.back-btn:focus {
  outline: none;
}
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.45);
  z-index: 2000;
  pointer-events: none;
}
.remember-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 3001;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 16px;
  box-shadow: 0 0 24px 8px rgba(79,209,197,0.15);
  padding: 2rem 2.5rem;
  color: #fff;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.2rem;
  width: 400px;
  max-width: 90vw;
  pointer-events: auto;
}
.remember-popup .nav-btn {
  margin: 1rem 0 0 0;
  width: 100%;
}
.remember-popup .alt {
  background: rgba(30,30,30,0.25);
  color: #4fd1c5;
  border: 1px solid #4fd1c5;
}
</style>
