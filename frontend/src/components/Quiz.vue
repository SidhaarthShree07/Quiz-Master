<template>
  <div class="dashboard-page-wrapper">
    <div ref="vantaBg" class="vanta-bg"></div>
    <div v-if="alreadyAttempted" class="quiz-content-centered">
      <div class="modal-box" style="margin-top: 20%;">
        <div class="modal-title">Quiz Attempted</div>
        <div class="modal-desc">You have already attempted the quiz.</div>
        <button class="quiz-btn" @click="() => router.push('/dashboard')">Go to Dashboard</button>
      </div>
    </div>
    <div v-else>
      <div class="quiz-content-centered" v-if="questions.length">
        <div class="quiz-header-row">
          <div class="quiz-timer-box">
            <span class="timer-label">Time Left</span>
            <span class="timer-value">{{ formattedTimer }}</span>
          </div>
          <div class="quiz-title">{{ quizName }}</div>
          <div class="quiz-question-count">
            <span>Question {{ currentQuestionIdx + 1 }} / {{ questions.length }}</span>
          </div>
        </div>
        <div class="quiz-question-box">
          <div class="question-statement">
            <template v-if="isImageQuestion(questions[currentQuestionIdx].question_statement)">
              <img :src="questions[currentQuestionIdx].question_statement" alt="Question Image" class="question-image" />
            </template>
            <template v-else>
              {{ questions[currentQuestionIdx].question_statement || questions[currentQuestionIdx].statement }}
            </template>
          </div>
          <div class="options-list">
            <div v-for="(opt, idx) in questions[currentQuestionIdx].options" :key="idx" class="option-row">
              <label :class="['option-label', selectedOption === idx ? 'selected' : '']">
                <input type="radio" :value="idx" v-model="selectedOption" />
                <span class="option-text">{{ opt }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="quiz-footer-row">
          <div class="score-box">Score: {{ questions[currentQuestionIdx].score ?? '-' }}</div>
          <button class="quiz-btn" @click="goToPrevQuestion" :disabled="currentQuestionIdx === 0">Previous</button>
          <button class="quiz-btn" @click="goToNextQuestion" :disabled="currentQuestionIdx === questions.length - 1">Save & Next</button>
          <button class="quiz-btn submit" @click="handleSubmit" :disabled="submitting">Submit</button>
        </div>
      </div>
      <div v-else class="quiz-content-centered"><div>Loading quiz...</div></div>
      <!-- Submit Success Modal -->
      <div v-if="showSubmitModal" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-title">Quiz Submitted!</div>
          <div class="modal-desc">Your quiz has been submitted successfully.</div>
        </div>
      </div>
      <!-- Review Modal -->
      <div v-if="showReviewModal" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-title">Rate Your Quiz Experience</div>
          <div class="modal-desc">How would you rate this quiz?</div>
          <div class="star-row">
              <span v-for="star in 5" :key="star"  @click="reviewRating = star" :class="['star', reviewRating >= star ? 'filled' : '']">&#9733;</span>
          </div>
          <div class="modal-actions">
            <button class="quiz-btn" @click="submitReview">Submit Rating</button>
            <button class="quiz-btn" @click="() => { showReviewModal = false; router.push('/dashboard') }">Ignore</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const quizName = ref(route.query.name ? route.query.name.replace(/\+/g, ' ') : 'Quiz')
const quizId = ref(route.params.quizId || (route.query.name ? route.query.name.replace(/\+/g, '_') : ''))
const userId = ref(route.params.userId || '')
const vantaBg = ref(null)
let vantaEffect = null

const quizDuration = ref(120) // seconds
const questions = ref([])
const currentQuestionIdx = ref(0)
const timer = ref(quizDuration.value)
const timerInterval = ref(null)
const showSubmitModal = ref(false)
const showReviewModal = ref(false)
const reviewRating = ref(0)
const submitting = ref(false)
const alreadyAttempted = ref(false)
const userQuizStatus = ref('')

// Store answers in sessionStorage
const getAnswerKey = (idx) => `quiz_${quizId.value}_q${idx}`
const selectedOption = ref(null)

const loadSelectedOption = () => {
  const key = getAnswerKey(currentQuestionIdx.value)
  const val = sessionStorage.getItem(key)
  selectedOption.value = val !== null ? Number(val) : null
}
const saveSelectedOption = () => {
  const key = getAnswerKey(currentQuestionIdx.value)
  if (selectedOption.value !== null) {
    sessionStorage.setItem(key, selectedOption.value)
  }
}

const goToNextQuestion = () => {
  saveSelectedOption()
  if (currentQuestionIdx.value < questions.value.length - 1) {
    currentQuestionIdx.value++
    loadSelectedOption()
  }
}
const goToPrevQuestion = () => {
  saveSelectedOption()
  if (currentQuestionIdx.value > 0) {
    currentQuestionIdx.value--
    loadSelectedOption()
  }
}
const handleSave = () => {
  saveSelectedOption()
}
const collectAnswers = () => {
  return questions.value.map((q, idx) => {
    const key = getAnswerKey(idx)
    const ans = sessionStorage.getItem(key)
    return {
      question_id: q.id,
      selected_option: ans !== null ? Number(ans) : null
    }
  })
}

// Submit answers to backend
const submitQuiz = async () => {
  if (submitting.value) return
  submitting.value = true
  // Always save the current selected option before collecting answers
  saveSelectedOption()
  const answers = collectAnswers()
  const payload = {
    user_id: userId.value,
    quiz_id: quizId.value,
    answers,
    timestamp: new Date().toISOString()
  }
  try {
    await axios.post('http://localhost:5000/api/user/submit-quiz', payload)
    showSubmitModal.value = true
    // After 1.5s, show review modal
    setTimeout(() => {
      showSubmitModal.value = false
      showReviewModal.value = true
    }, 1500)
  } catch (err) {
    alert('Failed to submit quiz. Please try again.')
  } finally {
    submitting.value = false
  }
}

const handleSubmit = () => {
  submitQuiz()
}

// Timer logic: auto submit when timer ends
watch(timer, (val) => {
  if (val === 0) {
    submitQuiz()
  }
})

// On refresh/unload, ensure backend submission using sendBeacon
window.addEventListener('beforeunload', (e) => {
  if (!showSubmitModal.value && !showReviewModal.value) {
    // Prepare payload
    const answers = collectAnswers()
    const payload = {
      user_id: userId.value,
      quiz_id: quizId.value,
      answers,
      timestamp: new Date().toISOString()
    }
    // Use sendBeacon for reliable submission
    const url = 'http://localhost:5000/api/user/submit-quiz'
    const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' })
    navigator.sendBeacon(url, blob)
  }
})

// Review modal submit
const submitReview = async () => {
  if (!reviewRating.value) {
    showReviewModal.value = false
    router.push('/dashboard')
    return
  }
  try {
    await axios.post('http://localhost:5000/api/user/submit-rating', {
      user_id: userId.value,
      quiz_id: quizId.value,
      rating: reviewRating.value
    })
    showReviewModal.value = false
    router.push('/dashboard')
  } catch (err) {
    alert('Failed to submit rating.')
    showReviewModal.value = false
    router.push('/dashboard')
  }
}

const fetchQuizDetails = async () => {
  // Only call API if quizId is present
  if (!quizId.value) {
    alert('Quiz ID missing. Redirecting to dashboard.')
    router.push('/dashboard')
    return
  }
  // Check UserQuiz status first
  try {
    const uqRes = await axios.get(`http://localhost:5000/api/user/user-quizzes/${userId.value}`)
    // Find quiz entry for this quiz
    const uq = uqRes.data.find(q => String(q.quiz_id) === String(quizId.value))
    if (!uq) {
      alert('You are not registered for this quiz.')
      router.push('/dashboard')
      return
    }
    userQuizStatus.value = uq.status
    console.log('UserQuiz status:', userQuizStatus.value)
    console.log('UserQuiz entry:', uq.status)
    if (uq.status !== 'booked') {
      alreadyAttempted.value = true
      return
    }
    // Proceed to fetch quiz details/questions
    console.log('fetchQuizDetails called, quizId:', quizId.value)
    const quizRes = await axios.get(`http://localhost:5000/api/user/quizzes/${quizId.value}`)
    quizName.value = quizRes.data.name
    quizDuration.value = quizRes.data.duration
    timer.value = quizDuration.value * 60 // duration in minutes
    const questionsRes = await axios.get(`http://localhost:5000/api/user/quizzes/${quizId.value}/questions`)
    questions.value = questionsRes.data
    loadSelectedOption()
  } catch (err) {
    console.error('Failed to fetch quiz:', err)
    alert('Failed to load quiz. Please try again later.')
    router.push('/dashboard')
  }
}

onMounted(() => {
  // Vanta background (same as UserDashboard)
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
  fetchQuizDetails()
  timerInterval.value = setInterval(() => {
    if (timer.value > 0) timer.value--
  }, 1000)
})

const formattedTimer = computed(() => {
  const min = Math.floor(timer.value / 60)
  const sec = timer.value % 60
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
})

const isImageQuestion = (statement) => {
  return typeof statement === 'string' && statement.startsWith('http://localhost:5000/api/user/uploads/question_images/')
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
.quiz-content-centered {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  min-width: 480px;
  max-width: 1000px;
  width: 100%;
  min-height: 700px;
  background: rgba(30, 30, 30, 0.22);
  color: #fff;
  border-radius: 32px;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.10);
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.quiz-header-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2.2rem;
}
.quiz-timer-box {
  background: rgba(79,209,197,0.10);
  border: 1.5px solid #4fd1c5;
  border-radius: 14px;
  padding: 0.7rem 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 110px;
}
.timer-label {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  color: #4fd1c5;
}
.timer-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.25rem;
  color: #fff;
  margin-top: 0.2rem;
}
.quiz-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5rem;
  color: #4fd1c5;
  text-align: center;
  flex: 1;
}
.quiz-question-count {
  background: rgba(79,209,197,0.10);
  border: 1.5px solid #4fd1c5;
  border-radius: 14px;
  padding: 0.7rem 1.2rem;
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  color: #4fd1c5;
  min-width: 110px;
  text-align: right;
}
.quiz-question-box {
  width: 100%;
  margin-bottom: 2.2rem;
}
.question-statement {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.18rem;
  color: #fff;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: start; /* default for text */
  align-items: center;
  text-align: left;
}
.options-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.option-row {
  width: 100%;
}
.option-label {
  display: flex;
  align-items: center;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.08rem;
  color: #fff;
  background: rgba(79,209,197,0.10);
  border: 1.5px solid #4fd1c5;
  border-radius: 12px;
  padding: 0.7rem 1.2rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.option-label.selected {
  background: #4fd1c5;
  color: #181c2f;
}
.option-label input[type="radio"] {
  margin-right: 1rem;
}
.option-text {
  flex: 1;
}
.quiz-footer-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.2rem;
  margin-top: 5.2rem;
}
.score-box {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  color: #4fd1c5;
  background: rgba(79,209,197,0.10);
  border: 1.5px solid #4fd1c5;
  border-radius: 14px;
  padding: 0.7rem 1.2rem;
  min-width: 110px;
}
.quiz-btn {
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
}
.quiz-btn:disabled {
  background: #232b3b;
  color: #4fd1c5;
  cursor: not-allowed;
}
.quiz-btn.submit {
  background: #232b3b;
  color: #4fd1c5;
}
.quiz-btn.submit:hover {
  background: #4fd1c5;
  color: #181c2f;
}
.question-image {
  max-width: 100%;
  max-height: 320px;
  border-radius: 16px;
  box-shadow: 0 2px 12px 0 rgba(79,209,197,0.18);
  display: block;
  margin: 0 auto;
  margin-bottom: 1.5rem;
}
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.45);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-box {
  background: #181c2f;
  border-radius: 24px;
  box-shadow: 0 2px 24px 0 rgba(79,209,197,0.18);
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  min-width: 320px;
  max-width: 400px;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.modal-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.4rem;
  color: #4fd1c5;
  margin-bottom: 1.2rem;
}
.modal-desc {
  font-size: 1.08rem;
  margin-bottom: 1.8rem;
  text-align: center;
}
.star-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.8rem;
}
.star {
  font-size: 2.2rem;
  color: #232b3b;
  cursor: pointer;
  transition: color 0.2s;
}
.star.filled {
  color: #ffe066;
  text-shadow: 0 0 8px #ffe066, 0 0 16px #ffd700;
}
.modal-actions {
  display: flex;
  gap: 1.2rem;
}
</style>
