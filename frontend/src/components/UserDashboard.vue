<template>
  <div v-if="isLoading" class="loader-overlay">
    <div class="loader">
      <div class="spinner"></div>
      <div class="loader-text">Loading...</div>
    </div>
  </div>
  <div class="dashboard-page-wrapper">
    <div ref="vantaBg" class="vanta-bg"></div>
    <div class="admin-layout">
      <div class="admin-sidebar">
        <div class="view-as-student-wrapper">
          <button v-if="isTeacher" class="view-as-student-btn" @click="goToAdminDashboard">View as Admin</button>
        </div>
        <div class="admin-navbar-container">
          <nav class="admin-navbar">
            <ul>
              <li :class="{active: selected==='home'}" @click="selected='home'">
                <span class="icon"><font-awesome-icon :icon="['fas', 'home']" /></span>
                <span>Home</span>
              </li>
              <li :class="{active: selected==='score'}" @click="selected='score'">
                <span class="icon"><font-awesome-icon :icon="['fas', 'trophy']" /></span>
                <span>Score</span>
              </li>
              <li :class="{active: selected==='stats'}" @click="selected='stats'">
                <span class="icon"><font-awesome-icon :icon="['fas', 'chart-bar']" /></span>
                <span>Statistics</span>
              </li>
              <li :class="{active: selected==='profile'}" @click="selected='profile'">
                <span class="icon"><font-awesome-icon :icon="['fas', 'user']" /></span>
                <span>Profile</span>
              </li>
              <li :class="{active: selected==='logout'}" @click="handleLogout">
                <span class="icon"><font-awesome-icon :icon="['fas', 'right-from-bracket']" /></span>
                <span>Logout</span>
              </li>
            </ul>
          </nav>
        </div>
      </div>
      <div class="main-content-vertical">
        <div v-if="selected !== 'profile' && selected !== 'stats'" class="admin-searchbar">
          <input type="text" placeholder="Search..." class="search-input" v-model="searchQuery" />
          <span class="search-icon"><font-awesome-icon :icon="['fas', 'search']" /></span>
          <span v-if="searchQuery" class="search-clear" @click="clearSearch">
            <font-awesome-icon :icon="['fas', 'xmark']" />
          </span>
        </div>
        <div v-if="selected === 'home' && !selectedSubject" class="home-subjects-box">
          <h2 class="home-heading">Choose a Subject to Start Your Quiz</h2>
          <div class="subjects-card-list">
            <div v-for="subject in filteredSubjects" :key="subject.id" class="subject-card" @click="selectSubject(subject)"
              :style="subject.color ? { border: '2px solid ' + subject.color, boxShadow: '0 0 16px 4px ' + subject.color } : {}">
              <img v-if="subject.image_file_name" :src="getSubjectImageUrl(subject.image_file_name)" class="subject-image" alt="Subject Image" />
              <div class="subject-name" :style="subject && subject.color ? { color: subject.color } : {}">{{ subject.name }}</div>
            </div>
          </div>
        </div>
        <div v-if="selected === 'home' && selectedSubject && !selectedChapter" class="chapter-select-box">
          <h2 class="home-heading">Choose a Chapter to Start Your Quiz</h2>
          <div class="chapters-card-list">
            <div v-for="chapter in filteredChapters" :key="chapter.id" class="chapter-card" @click="selectChapter(chapter)"
              :style="selectedSubject && selectedSubject.color ? { border: '2px solid ' + selectedSubject.color, boxShadow: '0 0 16px 4px ' + selectedSubject.color } : {}">
              <img v-if="chapter.image_file_name" :src="getChapterImageUrl(chapter.image_file_name)" class="chapter-image" alt="Chapter Image" />
              <div class="chapter-name" :style="selectedSubject && selectedSubject.color ? { color: selectedSubject.color } : {}">{{ chapter.name }}</div>
              <div class="chapter-quiz-count">Quizzes: {{ chapter.quiz_count }}</div>
            </div>
          </div>
          <button class="back-btn" @click="goBackToSubjects">Back</button>
        </div>
        <div v-if="selected === 'home' && selectedChapter" class="quizzes-table-box">
          <h2 class="home-heading">Upcoming Quizzes</h2>
          <table class="quizzes-table" v-if="filteredQuizzes.length > 0">
            <thead>
              <tr class="quizzes-table-header-row">
                <th class="quizzes-table-header first">ID</th>
                <th class="quizzes-table-header">Quiz Name</th>
                <th class="quizzes-table-header" style="max-width: 185px;">No. of Questions</th>
                <th class="quizzes-table-header">Date</th>
                <th class="quizzes-table-header">Duration</th>
                <th class="quizzes-table-header last">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(quiz, idx) in filteredQuizzes" :key="quiz.id">
                <td colspan="6" style="padding:0; border:none;">
                  <div class="quiz-row-box">
                    <div class="quiz-row-content">
                      <div class="quiz-row-item id">{{ idx + 1 }}</div>
                      <div class="quiz-row-item name">{{ quiz.name }}</div>
                      <div class="quiz-row-item count">{{ quiz.question_count }}</div>
                      <div class="quiz-row-item date">{{ formatQuizDate(quiz.date) }}</div>
                      <div class="quiz-row-item duration" style="padding-left:32px;">{{ quiz.duration }}</div>
                      <div class="quiz-row-item actions">
                        <template v-if="quiz.status === 'upcoming' && !quiz.userQuizStatus">
                          <button class="quiz-action-btn register" @click="openPaymentModal(quiz)">Register</button>
                        </template>
                        <template v-else-if="quiz.status === 'ongoing' && quiz.userQuizStatus === 'booked'">
                          <button class="quiz-action-btn register" @click="startQuiz(quiz)">Start Quiz</button>
                        </template>
                        <template v-else-if="quiz.status === 'upcoming' && quiz.userQuizStatus === 'booked'">
                          <button class="quiz-action-btn info" disabled>Booked</button>
                        </template>
                        <template v-else-if="quiz.status === 'ongoing' && quiz.userQuizStatus === 'attempted'">
                          <button class="quiz-action-btn register" disabled>Attempted</button>
                        </template>
                        <template v-else>
                          <button class="quiz-action-btn info" disabled>Not Registered</button>
                        </template>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else style="margin-top:2rem; color:#4fd1c5; font-family:'Orbitron',sans-serif; font-size:1.2rem;">No quizzes found for this chapter.</div>
          <div class="quizzes-table-footer">
            <button class="back-btn" @click="goBackToChapters">Back</button>
          </div>
        </div>
        <div v-if="showPaymentModal" class="payment-modal-overlay">
          <div class="payment-modal-box">
            <h2 class="payment-modal-title">Quiz Payment</h2>
            <div class="payment-modal-info">
              <div><strong>User:</strong> {{ userName }}</div>
              <div><strong>Quiz:</strong> {{ selectedQuizForPayment?.name }}</div>
              <div><strong>Amount:</strong> ₹{{ selectedQuizForPayment?.cost }}</div>
            </div>
           <div class="payment-modal-form">
              <input type="text" placeholder="Card Number" class="payment-input" maxlength="19" v-model="cardNumber" @input="formatCardNumber" />
              <input type="text" placeholder="Cardholder Name" class="payment-input" v-model="cardholderName" />
              <input type="text" placeholder="Expiry (MM/YY)" class="payment-input" maxlength="5" v-model="expiry" @input="formatExpiry" />
              <input type="password" placeholder="CVV" class="payment-input" maxlength="3" v-model="cvv" @input="limitCVV" />
            </div>
            <button class="pay-btn" @click="payForQuiz">Pay</button>
            <button class="close-btn" @click="closePaymentModal">Cancel</button>
          </div>
        </div>
        <div v-if="showSuccessPopup" class="success-popup">
          Successfully registered for quiz!
        </div>
        <div v-if="selected === 'score'" class="score-table-box">
          <h2 class="home-heading">Your Quiz Scores</h2>
          <table class="score-table" v-if="filteredScores.length > 0">
            <thead>
              <tr class="score-table-header-row">
                <th class="score-table-header first">ID</th>
                <th class="score-table-header">Quiz Name</th>
                <th class="score-table-header">No. of Questions</th>
                <th class="score-table-header">Status</th>
                <th class="score-table-header">Date</th>
                <th class="score-table-header">Score</th>
                <th class="score-table-header last">Ratings</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="score in filteredScores" :key="score.id">
                <td>{{ score.id }}</td>
                <td><div style="display: flex; justify-content: flex-start;margin-left: 15px;">{{ score.quizName }}</div></td>
                <td><div style="display: flex; justify-content: center; align-items: center;">{{ score.questionCount }}</div></td>
                <td>{{ score.status }}</td>
                <td>{{ score.date }}</td>
                <td><div style="display: flex; justify-content: center; align-items: center;">{{ score.score !== '-' ? `${score.score}/${score.totalScore}` : '-' }}</div></td>
                <td><div style="display: flex; justify-content: center; align-items: center;">{{ score.rating }}</div></td>
              </tr>
            </tbody>
          </table>
          <div v-else style="margin-top:2rem; color:#4fd1c5; font-family:'Orbitron',sans-serif; font-size:1.2rem;">No quiz scores found.</div>
        </div>
        <div v-if="selected === 'stats'">
          <div class="stats-dashboard-box" style="margin-top: 3.4rem;">
            <h2 class="home-heading">Your Quiz Statistics</h2>
            <div class="stats-charts-row">
              <div class="stats-chart-box">
                <h3 class="stats-chart-title">Subject-wise Quizzes Attempted</h3>
                <Bar
                  :data="{ labels: statsSubjectLabels, datasets: [{ label: 'Quizzes Attempted', data: statsSubjectData, backgroundColor: '#4fd1c5', borderRadius: 12 }] }"
                  :options="{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      title: { display: false }
                    },
                    scales: {
                      x: {
                        ticks: { color: '#fff' },
                        grid: {
                          display: false,
                          color: '#fff',
                        },
                        border: {
                          display: true,
                          color: '#fff'
                        }
                      },
                      y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0, color: '#fff' },
                        grid: {
                          display: false,
                          color: '#fff',
                        },
                        border: {
                          display: true,
                          color: '#fff'
                        }
                      }
                    }
                  }"
                  style="height: 340px; max-height: 340px;"
                />
              </div>
              <div class="stats-chart-box">
                <h3 class="stats-chart-title">Month-wise Quizzes Attempted</h3>
                <Line
                  :data="{ labels: statsMonthLabelsFormatted, datasets: [{ label: 'Quizzes Attempted', data: statsMonthData, borderColor: '#ffb347', backgroundColor: 'rgba(255,179,71,0.2)', tension: 0.3, fill: true, pointRadius: 6 }] }"
                  :options="{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: true, position: 'top' },
                      title: { display: false }
                    },
                    scales: {
                      x: {
                        ticks: { color: '#fff' },
                        grid: {
                          display: false,
                          color: '#fff',
                        },
                        border: {
                          display: true,
                          color: '#fff'
                        }
                      },
                      y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0, color: '#fff' },
                        grid: {
                          display: false,
                          color: '#fff',
                        },
                        border: {
                          display: true,
                          color: '#fff'
                        }
                      }
                    }
                  }"
                  style="height: 340px; max-height: 340px;"
                />
              </div>
              <div class="stats-chart-box">
                <h3 class="stats-chart-title">Average Score % per Subject</h3>
                <Bar
                  :data="{ labels: statsAvgScoreLabels, datasets: [{ label: 'Avg. Score %', data: statsAvgScoreData, backgroundColor: '#4fd1c5', borderRadius: 12 }] }"
                  :options="{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: true, position: 'top' },
                      title: { display: false }
                    },
                    scales: {
                      x: {
                        ticks: { color: '#fff' },
                        grid: { display: false, color: '#fff' },
                        border: { display: true, color: '#fff' }
                      },
                      y: {
                        beginAtZero: true,
                        ticks: { stepSize: 10, precision: 0, color: '#fff' },
                        grid: { display: false, color: '#fff' },
                        border: { display: true, color: '#fff' }
                      }
                    }
                  }"
                  style="height: 340px; max-height: 340px;"
                />
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
              <button class="export-csv-btn" @click="triggerExportCSV" :disabled="exportingCSV">
                <span v-if="!exportingCSV">Export Report as CSV</span>
                <span v-else>Exporting...</span>
              </button>
              <div v-if="csvReady" class="csv-alert">
                <div class="csv-download-link"><a :href="csvDownloadUrl" style="text-decoration: none; color: #181c2f;" target="_blank" download>Download the Report</a></div>
              </div>
            </div>
            <div v-if="exportingCSV && !csvReady" class="csv-alert">Export job running, please wait...</div>
          </div>
        </div>
        <div v-if="selected === 'profile'" class="profile-tab-box">
          <div class="profile-main">
            <div class="profile-image-box" @mouseenter="hoverImg=true" @mouseleave="hoverImg=false">
              <img :src="profileImageUrl" class="profile-image-square" @click="openProfileModal" alt="Profile Image" />
              <transition name="fade">
                <div v-if="hoverImg" class="profile-image-hover">Change Image</div>
              </transition>
            </div>
            <div class="profile-info-box">
              <div class="profile-row-side">
                <div class="profile-col">
                  <label>Username:</label>
                  <input :value="profileData.username" readonly class="profile-input readonly" />
                </div>
                <div class="profile-col">
                  <label>Role:</label>
                  <input :value="profileData.role" readonly class="profile-input readonly" />
                </div>
              </div>
              <div class="profile-row-side">
                <div class="profile-col">
                  <label>Name:</label>
                  <input v-model="profileEdit.name" :placeholder="profileData.name" class="profile-input" />
                </div>
                <div class="profile-col">
                  <label>Email:</label>
                  <input v-model="profileEdit.email" :placeholder="profileData.email" class="profile-input" />
                </div>
              </div>
              <div class="profile-row-side">
                <div class="profile-col">
                  <label>Date of Birth:</label>
                  <input type="date" v-model="profileEdit.dob" :placeholder="profileData.dob" class="profile-input" />
                </div>
                <div class="profile-col">
                  <label>Qualification:</label>
                  <select v-model="profileEdit.qualification" class="styled-select">
                    <option value="">Select</option>
                    <option value="Matriculate">Matriculate</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Diploma">Diploma</option>
                    <option value="Bachelor's Degree">Bachelor's Degree</option>
                    <option value="Master's Degree">Master's Degree</option>
                    <option value="Doctorate">Doctorate</option>
                  </select>
                </div>
              </div>
              <button class="profile-save-btn" @click="submitProfileEdit">Save Changes</button>
            </div>
          </div>
          <div v-if="showProfileModal" class="profile-modal-overlay">
            <div class="profile-modal-box-enhanced">
              <h3 class="profile-modal-title">Change Profile Image</h3>
              <input type="file" accept="image/*" @change="handleProfileImageChange" class="profile-modal-file" />
              <div class="profile-modal-btn-row">
                <button class="profile-modal-btn save" @click="submitProfileEdit">Upload & Save</button>
                <button class="profile-modal-btn cancel" @click="closeProfileModal">Cancel</button>
              </div>
            </div>
          </div>
        </div>
        <!-- You can add user dashboard content here -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { Bar, Line, Doughnut } from 'vue-chartjs'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { user } from '@/stores/user.js'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

import {
  Chart,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js';

Chart.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement, PointElement, LineElement);

// Chart.js global options for axis/tick color
Chart.defaults.color = '#fff';
Chart.defaults.plugins.legend.labels = { color: '#fff' };

const selected = ref('home')
const userId = computed(() => {
  // Try to get userId from user store first
  if (user.value?.username) {
    return user.value.username
  }
  // If not available, return empty string (will be fetched in watchers)
  return ''
})

// Function to get current user ID (with fallback)
const getCurrentUserId = async () => {
  // First try user store
  if (user.value?.username) {
    return user.value.username
  }
  // Fallback to API call
  try {
    const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
    return userRes.data.username
  } catch {
    return null
  }
}
const isLoading = ref(false)
const router = useRouter()
const vantaBg = ref(null)
let vantaEffect = null
const isTeacher = ref(false)
const subjects = ref([])
let subjectsInterval = null
const selectedSubject = ref(null)
const chapters = ref([])
const selectedChapter = ref(null)
const quizzes = ref([])
const showPaymentModal = ref(false)
const showSuccessPopup = ref(false)
const selectedQuizForPayment = ref(null)
const userName = ref('')
const cardNumber = ref('');
const cardholderName = ref('');
const expiry = ref('');
const cvv = ref('');
const userScores = ref([])
const statsSubjectLabels = ref([])
const statsSubjectData = ref([])
const statsMonthLabels = ref([])
const statsMonthData = ref([])
const statsAvgScoreLabels = ref([])
const statsAvgScoreData = ref([])
let hoverImg = ref(false)
const statsMonthLabelsFormatted = computed(() => statsMonthLabels.value.map(label => {
  // label format: '2025-07' => 'Jul 2025'
  const [year, month] = label.split('-')
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
  return `${monthNames[parseInt(month, 10) - 1]} ${year}`
}))
const searchQuery = ref('')

const filteredSubjects = computed(() => {
  if (!searchQuery.value.trim()) return subjects.value
  return subjects.value.filter(sub =>
    sub.name.toLowerCase().includes(searchQuery.value.trim().toLowerCase())
  )
})

const filteredChapters = computed(() => {
  if (!searchQuery.value.trim()) return chapters.value
  return chapters.value.filter(chap =>
    chap.name.toLowerCase().includes(searchQuery.value.trim().toLowerCase())
  )
})

const filteredQuizzes = computed(() => {
  if (!searchQuery.value.trim()) return quizzes.value
  return quizzes.value.filter(q => {
    const query = searchQuery.value.trim().toLowerCase()
    return (
      q.name.toLowerCase().includes(query) ||
      (q.date && q.date.toLowerCase().includes(query))
    )
  })
})

const filteredScores = computed(() => {
  if (!searchQuery.value.trim()) return userScores.value
  return userScores.value.filter(score => {
    const query = searchQuery.value.trim().toLowerCase()
    return (
      score.quizName.toLowerCase().includes(query) ||
      score.date.toLowerCase().includes(query) ||
      (score.score !== '-' && `${score.score}`.toLowerCase().includes(query))
    )
  })
})

const goToAdminDashboard = () => {
  router.push('/admin-dashboard')
}

const handleLogout = async () => {
  try {
    await axios.post('http://localhost:5000/api/auth/logout-session-only', {}, { withCredentials: true })
    window.location.href = '/'
  } catch (e) {
    window.location.href = '/'
  }
}

const getSubjectImageUrl = (filename) => {
  return `http://localhost:5000/api/user/uploads/subject_images/${filename}`
}
const getChapterImageUrl = (filename) => {
  return filename ? `http://localhost:5000/api/user/uploads/chapter_images/${filename}` : ''
}

const selectSubject = async (subject) => {
  isLoading.value = true
  selectedSubject.value = subject
  await fetchChapters(subject.id, true)
  isLoading.value = false
}
const goBackToSubjects = () => {
  selectedSubject.value = null
  chapters.value = []
}
const selectChapter = async (chapter) => {
  isLoading.value = true
  selectedChapter.value = chapter
  await fetchQuizzes(chapter.id, true)
  isLoading.value = false
}
const goBackToChapters = () => {
  selectedChapter.value = null
  quizzes.value = []
}

const fetchSubjects = async (showLoader = false) => {
  if (showLoader) isLoading.value = true
  try {
    const res = await axios.get('http://localhost:5000/api/user/subjects', { withCredentials: true })
    subjects.value = res.data
  } catch {
    subjects.value = []
  }
  if (showLoader) isLoading.value = false
}
const fetchChapters = async (subjectId, showLoader = false) => {
  if (showLoader) isLoading.value = true
  try {
    const res = await axios.get(`http://localhost:5000/api/user/subjects/${subjectId}/chapters`, { withCredentials: true })
    let chapterList = res.data
    // For each chapter, fetch quizzes and count only ongoing/upcoming
    const chapterPromises = chapterList.map(async (chapter) => {
      try {
        const quizRes = await axios.get(`http://localhost:5000/api/user/chapters/${chapter.id}/quizzes?status=UPCOMING,ONGOING`, { withCredentials: true })
        chapter.quiz_count = Array.isArray(quizRes.data) ? quizRes.data.length : 0
      } catch {
        chapter.quiz_count = 0
      }
      return chapter
    })
    chapters.value = await Promise.all(chapterPromises)
  } catch {
    chapters.value = []
  }
  if (showLoader) isLoading.value = false
}
const fetchQuizzes = async (chapterId, showLoader = false) => {
  if (showLoader) isLoading.value = true
  try {
    // Fetch quizzes for chapter
    const res = await axios.get(`http://localhost:5000/api/user/chapters/${chapterId}/quizzes?status=UPCOMING,ONGOING`, { withCredentials: true })
    let quizList = res.data
    // Fetch user id
    let userId = null
    try {
      const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
      userId = userRes.data.username
    } catch {}
    // Fetch UserQuiz records for user
    let userQuizMap = {}
    if (userId) {
      try {
        const uqRes = await axios.get(`http://localhost:5000/api/user/user-quizzes/${userId}`, { withCredentials: true })
        for (const uq of uqRes.data) {
          userQuizMap[uq.quiz_id] = uq.status
        }
      } catch {}
    }
    // Attach booking status to each quiz
    quizList = quizList.map(q => ({ ...q, userQuizStatus: userQuizMap[q.id] || null }))
    quizzes.value = quizList
  } catch (err) {
    console.error('Error fetching quizzes:', err)
    quizzes.value = []
  }
  if (showLoader) isLoading.value = false
}

const openPaymentModal = (quiz) => {
  selectedQuizForPayment.value = quiz
  showPaymentModal.value = true
}
const closePaymentModal = () => {
  showPaymentModal.value = false
}
const payForQuiz = async () => {
  if (!selectedQuizForPayment.value) return
  isLoading.value = true
  try {
    // Get user id from backend (assume user info endpoint)
    const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
    const userId = userRes.data.username
    userName.value = userRes.data.name || userRes.data.username
    // Call backend to register quiz
    await axios.post('http://localhost:5000/api/user/register-quiz', {
      quiz_id: selectedQuizForPayment.value.id,
      user_id: userId
    }, { withCredentials: true })
    showPaymentModal.value = false
    showSuccessPopup.value = true
    // Clear payment input refs
    cardNumber.value = '';
    cardholderName.value = '';
    expiry.value = '';
    cvv.value = '';
    setTimeout(() => {
      showSuccessPopup.value = false
    }, 2000)
    // Refresh upcoming quizzes after successful payment
    if (selectedChapter.value) {
      await fetchQuizzes(selectedChapter.value.id)
    }
  } catch (err) {
    alert('Payment failed or registration error.')
  }
  isLoading.value = false
}

const startQuiz = (quiz) => {
  // Redirect to Quiz.vue with quiz id and user id in path, and quiz name in query param
  const userId = user.value?.username || ''
  if (!userId) {
    axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true }).then(res => {
      const uid = res.data.username
      router.push({ path: `/quiz/${uid}/${quiz.id}`, query: { name: quiz.name } })
    })
  } else {
    router.push({ path: `/quiz/${userId}/${quiz.id}`, query: { name: quiz.name } })
  }
}

const fetchUserScores = async () => {
  isLoading.value = true
  try {
    // Get user id
    let userId = null
    try {
      const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
      userId = userRes.data.username
    } catch { /* Ignore user info fetch errors */ }
    if (!userId) return
    // Fetch all quiz scores for user from new backend API
    const scoresRes = await axios.get(`http://localhost:5000/api/user/user/quiz-scores/${userId}`)
    const scoresList = scoresRes.data
    userScores.value = scoresList.map((scoreObj, idx) => ({
      id: idx + 1,
      quizName: scoreObj.quiz_name,
      questionCount: scoreObj.question_count,
      status: scoreObj.status,
      date: scoreObj.date ? scoreObj.date.split('T')[0] : '',
      score: scoreObj.score !== null ? scoreObj.score : '-',
      totalScore: scoreObj.total_score,
      rating: scoreObj.rating !== null && scoreObj.rating !== undefined ? scoreObj.rating : 'Not Rated'
    }))
  } catch {
    // Ignore user scores fetch errors
    userScores.value = []
  }
  isLoading.value = false
}

const fetchStatistics = async () => {
  isLoading.value = true
  try {
    // Get user id
    let userId = null
    try {
      const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
      userId = userRes.data.username
    } catch { /* Ignore user info fetch errors */ }
    if (!userId) return
    // Fetch statistics data from new backend API
    const statsRes = await axios.get(`http://localhost:5000/api/user/user/quiz-statistics/${userId}`)
    const statsData = statsRes.data
    // Subject-wise statistics
    statsSubjectLabels.value = statsData.subjectWise.map(item => item.subject_name)
    statsSubjectData.value = statsData.subjectWise.map(item => item.attempted_count)
    // Month-wise statistics
    statsMonthLabels.value = statsData.monthWise.map(item => item.month)
    statsMonthData.value = statsData.monthWise.map(item => item.attempted_count)
    // Average score percentage
    statsAvgScoreLabels.value = statsData.avgScorePerSubject.map(item => item.subject_name)
    statsAvgScoreData.value = statsData.avgScorePerSubject.map(item => item.avg_score_percentage)
    // Debug: print chart data to console
    console.log('Average Score Chart Labels (reactive):', statsAvgScoreLabels.value)
    console.log('Average Score Chart Data (reactive):', statsAvgScoreData.value)
    // Print plain arrays for Chart.js
    console.log('Average Score Chart Labels (plain):', statsAvgScoreLabels.value.slice())
    console.log('Average Score Chart Data (plain):', statsAvgScoreData.value.slice())
  } catch {
    // Ignore statistics fetch errors
    statsSubjectLabels.value = []
    statsSubjectData.value = []
    statsMonthLabels.value = []
    statsMonthData.value = []
    statsAvgScoreLabels.value = []
    statsAvgScoreData.value = []
  }
  isLoading.value = false
}

// ...existing code...
const profileData = ref({})
const profileEdit = ref({})
const profileImageUrl = ref('')
const showProfileModal = ref(false)
const newProfileImage = ref(null)

async function fetchProfile() {
  try {
    const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
    const userId = userRes.data.username
    const res = await axios.get(`http://localhost:5000/api/user/profile/${userId}`)
    profileData.value = res.data
    profileEdit.value = {
      name: res.data.name || '',
      email: res.data.email || '',
      dob: res.data.dob || '',
      qualification: res.data.qualification || ''
    }
    profileImageUrl.value = `http://localhost:5000/api/user/uploads/user_images/${res.data.image_file_name}`
  } catch {
    profileData.value = {}
    profileImageUrl.value = 'http://localhost:5000/api/user/uploads/user_images/default.png'
  }
}

function openProfileModal() {
  showProfileModal.value = true
}
function closeProfileModal() {
  showProfileModal.value = false
  newProfileImage.value = null
}
function handleProfileImageChange(e) {
  if (e.target.files && e.target.files[0]) {
    newProfileImage.value = e.target.files[0]
  }
}
async function submitProfileEdit() {
  try {
    const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
    const userId = userRes.data.username
    const formData = new FormData()
    formData.append('name', profileEdit.value.name)
    formData.append('email', profileEdit.value.email)
    formData.append('dob', profileEdit.value.dob)
    formData.append('qualification', profileEdit.value.qualification)
    if (newProfileImage.value) {
      formData.append('image', newProfileImage.value)
    }
    await axios.put(`http://localhost:5000/api/user/profile/${userId}`, formData)
    await fetchProfile()
    closeProfileModal()
    window.location.reload()
  } catch {
    alert('Failed to update profile.')
  }
}

onMounted(async () => {
  // ...existing code...
  await fetchProfile()
})

// Always watch selected, but fetch userId from backend if not available
watch(selected, async (val) => {
  let currUserId = userId.value;
  
  // If userId is not available, try to fetch it from backend
  if (!currUserId) {
    currUserId = await fetchUserId()
    if (!currUserId) {
      return; // Exit if we can't get user ID
    }
  }
  
  console.log('[DEBUG] Tab changed:', { userId: currUserId, val });
  
  if (currUserId && val) {
    try {
      await axios.post('http://localhost:5000/api/user/active-tab', {
        user_id: currUserId,
        tab: val
      })
      console.log('[DEBUG] Active tab saved to Redis:', val);
    } catch {
      console.error('[DEBUG] Error calling active tab API');
    }
  } else {
    console.warn('[DEBUG] userId or val missing:', { userId: currUserId, val });
  }
  
  if (val === 'score') {
    fetchUserScores()
  } else if (val === 'stats') {
    fetchStatistics()
  }
})

// Restore active tab when userId becomes available
watch(userId, async (newUserId) => {
  if (newUserId) {
    try {
      const res = await axios.get(`http://localhost:5000/api/user/active-tab/${newUserId}`)
      if (res.data && res.data.tab) {
        selected.value = res.data.tab
      } else {
        selected.value = 'home'
      }
    } catch (e) {
      selected.value = 'home'
    }
  } else {
    // If userId is not available, try to fetch it from backend
    const fetchedUserId = await fetchUserId()
    if (fetchedUserId) {
      try {
        const res = await axios.get(`http://localhost:5000/api/user/active-tab/${fetchedUserId}`)
        if (res.data && res.data.tab) {
          selected.value = res.data.tab
        } else {
          selected.value = 'home'
        }
      } catch {
        selected.value = 'home'
      }
    } else {
      selected.value = 'home'
    }
  }
})

onMounted(async () => {
  // Vanta background
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
  
  // Fetch user info to determine role
  try {
    const res = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
    isTeacher.value = res.data.role === 'teacher'
    
    // Restore active tab after getting user info
    const userId = res.data.username
    console.log('[DEBUG] Current user ID:', userId)
    if (userId) {
      try {
        console.log('[DEBUG] Restoring active tab for user:', userId)
        const tabRes = await axios.get(`http://localhost:5000/api/user/active-tab/${userId}`)
        console.log('[DEBUG] Active tab API response:', tabRes.data)
        if (tabRes.data && tabRes.data.tab) {
          console.log('[DEBUG] Restored active tab:', tabRes.data.tab)
          selected.value = tabRes.data.tab
        } else {
          console.log('[DEBUG] No active tab found, using default: home')
          selected.value = 'home'
        }
      } catch {
        console.error('[DEBUG] Error restoring active tab')
        selected.value = 'home'
      }
    } else {
      console.log('[DEBUG] No user ID found')
    }
  } catch {
    console.error('[DEBUG] Error fetching user info')
    isTeacher.value = false
  }
  
  await fetchSubjects(true)
  // Fetch user info for payment modal
  try {
    const res = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
    userName.value = res.data.name || res.data.username
  } catch {}
  subjectsInterval = setInterval(() => fetchSubjects(false), 5000)
})
onBeforeUnmount(() => {
  if (vantaEffect) vantaEffect.destroy();
  if (subjectsInterval) clearInterval(subjectsInterval)
})
// Watch for tab changes and cache in backend


function formatCardNumber() {
  const digits = cardNumber.value.replace(/\D/g, '').substring(0, 16);
  const parts = digits.match(/.{1,4}/g);
  cardNumber.value = parts ? parts.join('-') : '';
}

function formatExpiry() {
  const digits = expiry.value.replace(/\D/g, '').substring(0, 4);
  if (digits.length >= 3) {
    expiry.value = digits.slice(0, 2) + '/' + digits.slice(2);
  } else {
    expiry.value = digits;
  }
}

function limitCVV() {
  cvv.value = cvv.value.replace(/\D/g, '').substring(0, 3);
}

function formatQuizDate(dateStr) {
  if (!dateStr) return '';
  // Accepts formats like '2025-07-27' or '2025-07-27T10:00:00Z'
  let d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  const day = d.getDate();
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const month = monthNames[d.getMonth()];
  return `${day} ${month}`;
}

function clearSearch() {
  searchQuery.value = ''
}

// Helper function to fetch user ID from backend
async function fetchUserId() {
  try {
    const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
    return userRes.data.username
  } catch (err) {
    console.error('[DEBUG] Error fetching user ID:', err)
    return null
  }
}

const exportingCSV = ref(false)
const csvReady = ref(false)
const csvDownloadUrl = ref('')

async function triggerExportCSV() {
  exportingCSV.value = true
  csvReady.value = false
  try {
    // Get user ID from the API
    const userRes = await axios.get('http://localhost:5000/api/admin/user/info', { withCredentials: true })
    const userId = userRes.data.username
    
    if (!userId) {
      exportingCSV.value = false
      alert('Could not get user ID. Please try again.')
      return
    }
    
    const res = await axios.post('http://localhost:5000/api/user/export-csv', { user_id: userId })
    if (res.data && res.data.status === 'done') {
      // Handle current response format with download URL
      if (res.data.download_url) {
        // Create full download URL
        const downloadUrl = `http://localhost:5000${res.data.download_url}`
        
        // Set the download URL for the frontend
        csvDownloadUrl.value = downloadUrl
        csvReady.value = true
        exportingCSV.value = false
        
        // Extract filename for user feedback
        const filename = res.data.download_url.split('/').pop()
        alert(`CSV export completed! File: ${filename}`)

        console.log(`CSV file created: ${filename}`)
        console.log(`Download URL: ${downloadUrl}`)
        console.log(`File location: backend/exports/${filename}`)
      } else {
        exportingCSV.value = false
        alert('Export completed but no download URL received.')
      }
    } else if (res.data && res.data.task_id) {
      // Async execution (for future Celery implementation)
      pollCSVStatus(res.data.task_id)
    } else {
      exportingCSV.value = false
      alert('Failed to start export job.')
    }
  } catch {
    exportingCSV.value = false
    alert('Error starting export job.')
  }
}

async function pollCSVStatus(taskId) {
  let attempts = 0
  const maxAttempts = 20
  const pollInterval = 2000
  while (attempts < maxAttempts) {
    try {
      const res = await axios.get(`http://localhost:5000/api/user/export-csv-status/${taskId}`)
      if (res.data && res.data.status === 'done') {
        csvDownloadUrl.value = res.data.download_url
        csvReady.value = true
        exportingCSV.value = false
        alert('CSV export completed!')
        return
      }
    } catch {
      // Ignore export errors
      exportingCSV.value = false
      alert('Export failed. Please try again.')
    }
    attempts++;
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
  exportingCSV.value = false
  alert('Export job timed out.')
}
</script>

<style scoped>
.dashboard-page-wrapper {
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
.admin-layout {
  display: flex;
  height: 90vh;
  align-items: center;
  position: relative;
  z-index: 1;
  margin-left: 2.5rem;
  margin-right: 2.5rem;
  margin-top: 2.5rem;
  margin-bottom: 2.5rem;
}
.admin-sidebar {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-width: 250px;
  margin-right: 2.5rem;
  height: 100%;
}
.view-as-student-wrapper {
  width: 100%;
  display: flex;
  margin-top: 2.5rem;
  justify-content: center;
}
.view-as-student-btn {
  background: rgba(79,209,197,0.18);
  color: #4fd1c5;
  border: 1.5px solid rgba(79,209,197,0.28);
  border-radius: 18px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  margin-bottom: 0.5rem;
}
.view-as-student-btn:hover {
  background: #4fd1c5;
  color: #181c2f;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.18);
}
.admin-navbar-container {
  width: 250px;
  min-width: 220px;
  height: 520px;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 32px;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.10);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem 2rem 1.5rem;
  position: relative;
  z-index: 1;
  margin-top: 4.5rem;
  border: 1.5px solid rgba(79,209,197,0.18);
}
.admin-navbar {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}
.admin-navbar ul {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1.1rem;
}
.admin-navbar li {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.18rem;
  color: #fff;
  width: 100%;
  height: 56px;
  padding: 0 1.2rem;
  border-radius: 18px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  background: rgba(255,255,255,0.04);
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.04);
  justify-content: flex-start;
}
.admin-navbar li:last-child {
  margin-bottom: 0;
}
.admin-navbar li.active, .admin-navbar li:hover {
  background: rgba(79,209,197,0.18);
  color: #4fd1c5;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
}
.admin-navbar .icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.main-content-vertical {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;
  justify-content: flex-start;
  margin-right: 0;
  margin-top: 0;
  min-height: 700px;
  min-width: 700px;
  flex: 1;
  background: rgba(30, 30, 30, 0.18);
  color: #fff;
  position: relative;
  z-index: 1;
  border-radius: 32px;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.10);
  padding-top: 0;
}
.admin-searchbar {
  width: 540px;
  margin-top: 2.5rem;
  margin-bottom: 2.5rem;
  display: flex;
  align-items: center;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 18px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 0.7rem 1.5rem;
  position: relative;
  margin-left: auto;
  margin-right: auto;
}
.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  padding: 0.2rem 0.5rem;
}
.search-input::placeholder {
  color: #4fd1c5bb;
  font-family: 'Orbitron', sans-serif;
}
.search-icon {
  font-size: 1.3rem;
  color: #4fd1c5;
  margin-left: 0.7rem;
  z-index: 2;
  cursor: pointer;
  position: relative;
}
.search-clear {
  cursor: pointer;
  margin-left: 1rem;
  color: #ff1744;
  font-size: 1.7rem;
  z-index: 3;
  position: relative;
}
.home-subjects-box {
  width: 100%;
  max-width: 700px;
  margin: 2.5rem auto 0 auto;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.home-heading {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.7rem;
  color: #4fd1c5;
  margin-bottom: 2rem;
  text-align: center;
}
.subjects-card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 2.5rem;
  justify-content: center;
  width: 100%;
}
.subject-card,
.chapter-card {
  background: rgba(30, 30, 30, 0.22);
  border-radius: 18px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 1.2rem 1.2rem 1.2rem 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 180px;
  min-height: 220px;
  margin-bottom: 1.5rem;
  cursor: pointer;
  transition: box-shadow 0.2s, border 0.2s, background 0.2s;
}
.subject-card:hover,
.chapter-card:hover {
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.18);
  border: 2px solid #4fd1c5;
  background: rgba(79,209,197,0.10);
}
.subject-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
  margin-bottom: 1rem;
  box-shadow: 0 0 8px 2px rgba(79,209,197,0.10);
}
.subject-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  color: #4fd1c5;
  text-align: center;
  margin-top: 0.5rem;
}
.chapter-select-box {
  position: relative;
  width: 100%;
  max-width: 700px;
  margin: 2.5rem auto 0 auto;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.chapters-card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 2.5rem;
  justify-content: center;
  width: 100%;
}
.chapter-card {
  background: rgba(30, 30, 30, 0.22);
  border-radius: 18px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 1.2rem 1.2rem 1.2rem 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 180px;
  min-height: 220px;
  margin-bottom: 1.5rem;
}
.chapter-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
  margin-bottom: 1rem;
  box-shadow: 0 0 8px 2px rgba(79,209,197,0.10);
}
.chapter-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  color: #4fd1c5;
  text-align: center;
  margin-top: 0.5rem;
}
.chapter-quiz-count {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  color: #fff;
  margin-top: 0.3rem;
  text-align: center;
}
.back-btn {
  position: absolute;
  left: 2.5rem;
  bottom: 2rem;
  background: #4fd1c5;
  color: #181c2f;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s;
  margin-bottom: 0;
}
.back-btn:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.quizzes-table-box {
  position: relative;
  width: 100%;
  max-width: 1200px;
  margin: 2.5rem auto 0 auto;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 32px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.quizzes-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 1.2rem;
  margin-top: 1.5rem;
}
.quizzes-table-header-row {
  background: none;
}
.quizzes-table-header {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  color: #4fd1c5;
  font-weight: 600;
  background: rgba(79,209,197,0.10);
  border: none;
  padding: 1.1rem 1.2rem;
  text-align: left;
}
.quizzes-table-header.first {
  border-top-left-radius: 18px;
}
.quizzes-table-header.last {
  border-top-right-radius: 18px;
}
.quiz-row-box {
  background: rgba(30, 30, 30, 0.32);
  border-radius: 18px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 1.1rem 1.2rem;
  margin-bottom: 0.2rem;
  display: flex;
  align-items: center;
  width: 100%;
}
.quiz-row-content {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 2.2rem;
}
.quiz-row-item {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  color: #fff;
  text-align: left;
  display: flex;
  align-items: center;
}
.quiz-row-item.id { width: 60px; justify-content: flex-start; }
.quiz-row-item.name { width: 200px; font-weight: 600; color: #4fd1c5; }
.quiz-row-item.count { width: 120px; display: flex; justify-content: center; align-items: center; }
.quiz-row-item.date { width: 200px; justify-content: flex-end;}
.quiz-row-item.duration { width: 120px; padding-left: 32px; justify-content: flex-end; }
.quiz-row-item.actions { width: 180px; display: flex; gap: 1rem; justify-content: flex-end; }
.quiz-action-btn {
  margin-right: 0;
  padding: 0.5rem 1.5rem;
  border-radius: 12px;
  border: none;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
}
.quiz-action-btn.info {
  background: #232b3b;
  color: #4fd1c5;
}
.quiz-action-btn.register {
  background: #4fd1c5;
  color: #232b3b;
}
.quiz-action-btn.info:hover {
  background: #4fd1c5;
  color: #181c2f;
}
.quiz-action-btn.register:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.quizzes-table-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2.5rem;
}
.back-btn {
  position: static;
  background: #4fd1c5;
  color: #181c2f;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s;
  margin-bottom: 0;
  margin-top: 0;
}
.back-btn:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.payment-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(30,30,30,0.55);
  backdrop-filter: blur(8px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}
.payment-modal-box {
  background: rgba(30,30,30,0.98);
  border-radius: 24px;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.18);
  border: 2px solid #4fd1c5;
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  min-width: 400px;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.payment-modal-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5rem;
  color: #4fd1c5;
  margin-bottom: 1.5rem;
}
.payment-modal-info {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  color: #fff;
  margin-bottom: 1.5rem;
  width: 100%;
}
.payment-modal-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}
.payment-input {
  background: rgba(79,209,197,0.10);
  border: 1.5px solid #4fd1c5;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  color: #fff;
  padding: 0.7rem 1.2rem;
  outline: none;
}
.pay-btn {
  background: #4fd1c5;
  color: #181c2f;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s;
  margin-bottom: 0.7rem;
}
.pay-btn:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.close-btn {
  background: #232b3b;
  color: #4fd1c5;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s;
}
.close-btn:hover {
  background: #4fd1c5;
  color: #181c2f;
}
.success-popup {
  position: fixed;
  top: 20%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #4fd1c5;
  color: #181c2f;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.3rem;
  border-radius: 18px;
  padding: 1.2rem 2.5rem;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.18);
  z-index: 200;
}
.user-scores-box {
  width: 100%;
  max-width: 800px;
  margin: 2.5rem auto;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.no-scores-message {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  color: #fff;
  text-align: center;
  margin-top: 1.5rem;
}
.user-scores-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1.5rem;
}
.user-score-item {
  background: rgba(30, 30, 30, 0.32);
  border-radius: 18px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  width: 100%;
}
.user-score-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.user-score-quiz-name {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.2rem;
  color: #4fd1c5;
}
.user-score-info {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  color: #fff;
  display: flex;
  justify-content: space-between;
}
/* Loader styles */
.loader-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(30,30,30,0.55);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.spinner {
  width: 64px;
  height: 64px;
  border: 7px solid #4fd1c5;
  border-top: 7px solid #232b3b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.2rem;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.loader-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.25rem;
  color: #4fd1c5;
  text-align: center;
}
.score-table-box {
  position: relative;
  width: 100%;
  max-width: 1200px;
  margin: 2.5rem auto 0 auto;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 32px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.score-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 1.2rem;
  margin-top: 1.5rem;
}
.score-table-header-row {
  background: none;
}
.score-table-header {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  color: #4fd1c5;
  font-weight: 600;
  background: rgba(79,209,197,0.10);
  border: none;
  padding: 1.1rem 1.2rem;
  text-align: left;
}
.score-table-header.first {
  border-top-left-radius: 18px;
}
.score-table-header.last {
  border-top-right-radius: 18px;
}
.score-table tbody tr {
  background: none;
}
.score-table td {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  color: #fff;
  border-radius: 18px;
  padding: 1.1rem 1.2rem;
  margin-bottom: 0.2rem;
}
.stats-dashboard-box {
  width: 100%;
  max-width: 1200px;
  margin: 2.5rem auto;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 32px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stats-charts-row {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: center;
  margin-top: 1.5rem;
}
.stats-chart-box {
  background: rgba(30, 30, 30, 0.32);
  border-radius: 18px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 1.1rem 1.2rem;
  margin-bottom: 0.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 340px;
  height: 450px;
}
.stats-chart-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.18rem;
  color: #4fd1c5;
  font-weight: 600;
  margin-bottom: 1.2rem;
  text-align: center;
}
.export-csv-btn {
  background: #4fd1c5;
  color: #181c2f;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s;
  margin-top: 3.4rem;
}

.csv-download-link{
  background: #4fd1c5;
  color: #181c2f;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s;
  margin-top: 2.2rem;
}
.export-csv-btn:disabled {
  background: #232b3b;
  color: #4fd1c5;
  cursor: not-allowed;
}
.csv-alert {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.15rem;
  color: #4fd1c5;
  margin-top: 1.2rem;
}

.profile-tab-box {
  width: 100%;
  max-width: 1000px;
  height: 500px;
  margin: auto auto auto auto;
  background: rgba(30, 30, 30, 0.22);
  border-radius: 24px;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  border: 1.5px solid rgba(79,209,197,0.18);
  padding: 2.2rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.profile-main {
  display: flex;
  gap: 2.5rem;
  align-items: flex-start;
}
.profile-image-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-right: 2.5rem;
}
.profile-image {
  width: 140px;
  height: 140px;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 0 8px 2px rgba(79,209,197,0.10);
  cursor: pointer;
  border: 2px solid #4fd1c5;
}
.profile-image-hint {
  font-size: 0.95rem;
  color: #4fd1c5;
  margin-top: 0.7rem;
}
.profile-info-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.profile-row {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}
.profile-input {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(79,209,197,0.18);
  border-radius: 10px;
  color: #fff;
  font-family: 'Orbitron', sans-serif;
  padding: 0.5rem 0.8rem;
  outline: none;
  transition: border 0.2s;
  flex: 1;
  font-size: 1.08rem;
}
.profile-input.readonly {
  background: #232b3b;
  color: #4fd1c5;
  border: none;
}
.profile-save-btn {
  margin-top: 1.5rem;
  background: #4fd1c5;
  color: #232b3b;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s;
}
.profile-save-btn:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.profile-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}



.profile-image-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}
.profile-image-square {
  width: 140px;
  height: 140px;
  object-fit: cover;
  border-radius: 18px;
  box-shadow: 0 0 8px 2px rgba(79,209,197,0.10);
  cursor: pointer;
  border: 2px solid #4fd1c5;
  transition: box-shadow 0.2s, border 0.2s;
}
.profile-image-square:hover {
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.18);
  border: 2.5px solid #4fd1c5;
}
.profile-image-hover {
  position: absolute;
  top: 0;
  left: 0;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30,30,30,0.65);
  color: #4fd1c5;
  font-size: 1rem;
  font-family: 'Orbitron', sans-serif;
  border-radius: 18px;
  pointer-events: none;
  z-index: 2;
  transition: background 0.2s;
}

.styled-select {
  background: #4fd1c5;
  border: 1px solid rgba(79,209,197,0.28);
  border-radius: 10px;
  color: #181c2f;
  font-size: 1rem;
  font-family: 'Orbitron', sans-serif;
  padding: 0.5rem 0.8rem;
  outline: none;
  transition: border 0.2s;
  width: 100%;
}
.styled-select:focus {
  border: 1.5px solid #232b3b;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.profile-row-side {
  display: flex;
  gap: 2.2rem;
  margin-bottom: 1.2rem;
}
.profile-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.profile-col label{
  color: #fff;
  font-size: 1rem;
  font-family: 'Orbitron', sans-serif;
}
.profile-modal-box-enhanced {
  background: #232b3b;
  border-radius: 18px;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.18);
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2rem;
  min-width: 340px;
}
.profile-modal-title {
  font-size: 1.3rem;
  color: #4fd1c5;
  margin-bottom: 1.2rem;
  font-family: 'Orbitron', sans-serif;
}
.profile-modal-file {
  margin-bottom: 1.2rem;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  border: 1.5px solid #4fd1c5;
  background: rgba(30,30,30,0.12);
  color: #fff;
  font-size: 1.08rem;
}
.profile-modal-btn-row {
  display: flex;
  gap: 1.5rem;
  margin-top: 1.2rem;
}
.profile-modal-btn {
  background: #4fd1c5;
  color: #232b3b;
  border: none;
  border-radius: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  padding: 0.7rem 2.2rem;
  cursor: pointer;
  box-shadow: 0 2px 8px 0 rgba(79,209,197,0.08);
  transition: background 0.2s, color 0.2s;
}
.profile-modal-btn.save:hover {
  background: #232b3b;
  color: #4fd1c5;
}
.profile-modal-btn.cancel {
  background: #ff1744;
  color: #fff;
}
.profile-modal-btn.cancel:hover {
  background: #232b3b;
  color: #ff1744;
}

</style>
