<template>
  <div class="page-wrapper">
    <div ref="vantaBg" class="vanta-bg"></div>
    <div class="register-content">
      <div class="register-container">
        <h2 class="register-headline">Register</h2>
        <form @submit.prevent="registerUser">
          <div class="form-group">
            <label for="name">Full Name</label>
            <input v-model="form.name" id="name" required placeholder="Enter your full name" />
          </div>
          <div class="form-group">
            <label for="username">Username</label>
            <input v-model="form.username" id="username" required
                   :class="{ 'input-error': usernameTaken }"
                   @input="checkUsername" placeholder="Enter username" />
            <div v-if="usernameTaken" class="error">Username is already taken.</div>
          </div>
          <div class="form-group password-group">
            <label for="password">Password</label>
            <div class="password-icon-group">
              <input v-model="form.password" :type="showPassword ? 'text' : 'password'" id="password" required placeholder="Enter password" />
              <span class="icon-eye" @click.stop="toggleShowPassword" tabindex="0">
                <font-awesome-icon v-if="!showPassword" :icon="['fas', 'eye']" style="color: #4fd1c5; margin-bottom: 1rem; font-size: 1.5rem; vertical-align: middle;" />
                <font-awesome-icon v-else :icon="['fas', 'eye-slash']" style="color: #4fd1c5; margin-bottom: 1rem; font-size: 1.5rem; vertical-align: middle;" />
              </span>
            </div>
          </div>
          <button type="submit" :disabled="usernameTaken">Register</button>
          <div v-if="error" class="error">{{ error }}</div>
        </form>
        <div v-if="showSuccess" class="success-popup">
          <div class="success-content">
            <h3>Registration Successful!</h3>
            <button @click="goToLogin">Go to Login</button>
          </div>
        </div>
      </div>
    </div>
    <button class="back-btn" @click="goBack" @mouseenter="isHoveringBack = true" @mouseleave="isHoveringBack = false">
      <font-awesome-icon :icon="['fas', 'angles-left']" :fade="isHoveringBack" style="color: #ffffff; font-size: 2.2rem;" />
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const form = ref({
  username: '',
  password: '',
  name: ''
})
const error = ref('')
const usernameTaken = ref(false)
let usernameCheckTimeout = null
const showPassword = ref(false)
const showSuccess = ref(false)
const router = useRouter()
const vantaBg = ref(null)
let vantaEffect = null
const isHoveringBack = ref(false)

function toggleShowPassword() {
  showPassword.value = !showPassword.value
}

function validatePassword(password) {
  // At least 8 chars, one letter, one number, one special char
  return /^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$/.test(password)
}

const checkUsername = () => {
  usernameTaken.value = false
  if (usernameCheckTimeout) clearTimeout(usernameCheckTimeout)
  if (!form.value.username) return
  usernameCheckTimeout = setTimeout(async () => {
    try {
      const res = await axios.get(`http://localhost:5000/api/user/check-username`, { params: { username: form.value.username } })
      usernameTaken.value = !res.data.available
    } catch {
      usernameTaken.value = false
    }
  }, 400)
}

const registerUser = async () => {
  error.value = ''
  if (!validatePassword(form.value.password)) {
    error.value = 'Password must be at least 8 characters, include a letter, a number, and a special character.'
    return
  }
  if (usernameTaken.value) {
    error.value = 'Username is already taken.'
    return
  }
  try {
    await axios.post('http://localhost:5000/api/user/register', form.value)
    showSuccess.value = true
  } catch (err) {
    error.value = err.response?.data?.message || 'Registration failed.'
  }
}

function goToLogin() {
  router.push('/login')
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

onMounted(() => {
  const tryInit = () => {
    if (window.VANTA && window.VANTA.TOPOLOGY) {
      vantaEffect = window.VANTA.TOPOLOGY({
        el: vantaBg.value,
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
})
onBeforeUnmount(() => {
  if (vantaEffect) vantaEffect.destroy();
})
</script>

<script>
export default {
  name: 'UserRegister',
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css?family=Montserrat:400,700');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
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
.register-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.register-container {
  width: 440px;
  min-width: 440px;
  max-width: 440px;
  height: 540px;
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
.register-headline {
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
.form-group {
  margin-bottom: 1rem;
}
label {
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
  border: 2px solid #888;
  margin-bottom: 1rem;
  padding: calc(0.5rem - 1px);
  transition: border-color 0.2s;
  box-sizing: border-box;
}
input:focus, .form-control:focus {
  outline: none;
  border-color: #4fd1c5;
}
.form-group input,
.password-icon-group input {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
}
.password-group {
  position: relative;
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
  color: #4fd1c5;
  display: flex;
  align-items: center;
  height: 100%;
  background: transparent;
  pointer-events: auto;
}
.icon-eye:active, .icon-eye:focus {
  outline: none;
}
button[type="submit"], .nav-btn {
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
button[type="submit"]:disabled {
  background: #aaa;
  cursor: not-allowed;
}
button[type="submit"]:hover, .nav-btn:hover {
  background: rgba(79, 209, 197, 0.18);
  color: #4fd1c5;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.18) inset, 0 0 16px 4px rgba(79,209,197,0.10);
}
.error {
  color: #e74c3c;
  margin-top: 1rem;
}
.success-popup {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.success-content {
  background: #fff;
  padding: 2rem 2.5rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(31,38,135,0.37);
  text-align: center;
}
.success-content h3 {
  margin-bottom: 1.5rem;
  color: #2d8cf0;
}
.success-content button {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 8px;
  background: #2d8cf0;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.success-content button:hover {
  background: #1a73e8;
}
.back-btn {
  position: fixed;
  top: 2.5rem;
  left: 2.5rem;
  z-index: 9999;
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
</style>
