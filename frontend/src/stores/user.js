import { ref } from 'vue'
import axios from 'axios'

export const user = ref(null)

export async function tryAutoLogin() {
  const token = localStorage.getItem('remember_token')
  if (token) {
    try {
      const res = await axios.post('http://localhost:5000/api/auth/me', { token })
      user.value = res.data
    } catch {
      user.value = null
      localStorage.removeItem('remember_token')
    }
  } else {
    user.value = null
  }
}

export function logout() {
  localStorage.removeItem('remember_token')
  user.value = null
}
