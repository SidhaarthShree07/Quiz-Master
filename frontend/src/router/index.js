import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/HomeView.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import UserDashboard from '../components/UserDashboard.vue'
import AdminDashboard from '../components/AdminDashboard.vue'
import Quiz from '../components/Quiz.vue'
import StatsView from '../components/Stats.vue'
import axios from 'axios'

const routes = [
  { path: '/', name: 'HomeView', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/dashboard', name: 'UserDashboard', component: UserDashboard },
  { path: '/admin-dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresTeacher: true } },
  { path: '/quiz/:userId/:quizId', name: 'Quiz', component: Quiz },
  { path: '/stats', name: 'StatsView', component: StatsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresTeacher) {
    try {
      const res = await axios.get('http://localhost:5000/api/user/dashboard', { withCredentials: true })
      if (res.data.dashboard_type !== 'admin') {
        return next('/login')
      }
    } catch {
      return next('/login')
    }
  }
  next()
})

// Add helper for quiz navigation
export function goToQuiz(router, quiz) {
  // quiz should have id and name
  router.push({ path: '/quiz', query: { id: quiz.id, name: quiz.name } })
}

export default router
