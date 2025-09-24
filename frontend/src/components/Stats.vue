<template>
  <div class="dashboard-page-wrapper">
    <div ref="vantaBg" class="vanta-bg"></div>
    <div class="stats-content">
      <div class="stats-header-row">
        <div class="stats-heading-box">
          <h1 class="dashboard-title">Statistics</h1>
        </div>
        <div class="stats-summary-row">
          <div class="stats-card glass-card stat-card">
            <div class="stat-title">Total Users</div>
            <div class="stat-value">{{ summary.total_users }}</div>
          </div>
          <div class="stats-card glass-card stat-card">
            <div class="stat-title">Total Quizzes</div>
            <div class="stat-value">{{ summary.total_quizzes }}</div>
          </div>
          <div class="stats-card glass-card stat-card">
            <div class="stat-title">Average Quiz Rating</div>
            <div class="stat-value">{{ summary.avg_rating }}</div>
          </div>
        </div>
      </div>
      <div class="stats-charts-row">
        <div class="stats-card glass-card chart-card">
          <div class="chart-title">Top Scorer by Subject</div>
          <canvas id="subjectTopScorerChart"></canvas>
        </div>
        <div class="stats-card glass-card chart-card">
          <div class="chart-title">Quiz Attempts by Subject</div>
          <canvas id="subjectQuizAttemptsChart"></canvas>
        </div>
        <div class="stats-card glass-card chart-card">
          <div class="chart-title">Monthly Revenue</div>
          <canvas id="monthlyRevenueChart"></canvas>
        </div>
      </div>
    </div>
    <footer class="dashboard-footer">
      <button class="back-btn" @click="goBackToAdminDashboard">Back to Admin Dashboard</button>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'
import { useRouter } from 'vue-router'

const vantaBg = ref(null)
let vantaEffect = null

const summary = ref({ total_users: 0, total_quizzes: 0, avg_rating: 0 })
let subjectTopScorerChart = null
let subjectQuizAttemptsChart = null
let monthlyRevenueChart = null
const router = useRouter()

onMounted(async () => {
  await nextTick();
  const tryInit = () => {
    if (window.VANTA && window.VANTA.TOPOLOGY && vantaBg.value) {
      if (vantaEffect) vantaEffect.destroy();
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

  // Fetch stats summary
  const summaryRes = await axios.get('http://localhost:5000/api/admin/stats/summary', { withCredentials: true })
  summary.value = summaryRes.data

  // Subject top scorer chart
  const topScorerRes = await axios.get('http://localhost:5000/api/admin/stats/subject-top-scorers', { withCredentials: true })
  const topScorerData = topScorerRes.data
  const topScorerLabels = topScorerData.map(d => d.subject)
  // For each subject, get top 3 scorers and their percent
  const topScorerBars = topScorerData.map(d => {
    if (!d.top_scorers || d.top_scorers.length === 0) return { label: 'N/A', percent: 0 }
    // Show top scorer's percent as bar value, but tooltip will show all top 3
    return { label: d.top_scorers[0].username, percent: d.top_scorers[0].percent, top3: d.top_scorers }
  })
  if (subjectTopScorerChart) subjectTopScorerChart.destroy()
  subjectTopScorerChart = new Chart(document.getElementById('subjectTopScorerChart'), {
    type: 'bar',
    data: {
      labels: topScorerLabels,
      datasets: [{
        label: '',
        data: topScorerBars.map(b => b.percent),
        backgroundColor: '#4fd1c5',
      }]
    },
    options: {
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const bar = topScorerBars[context.dataIndex]
              if (!bar.top3) return 'No data'
              return bar.top3.map((u, i) => `${i+1}. ${u.username}: ${u.percent}%`).join(' | ')
            }
          }
        }
      },
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  })

  // Subject quiz attempts chart
  const attemptsRes = await axios.get('http://localhost:5000/api/admin/stats/subject-quiz-attempts', { withCredentials: true })
  const attemptsData = attemptsRes.data
  const attemptsLabels = attemptsData.map(d => d.subject)
  // For each subject, sum all users' attempts
  const attemptsTotals = attemptsData.map(d => Object.values(d.attempts).reduce((a, b) => a + b, 0))
  if (subjectQuizAttemptsChart) subjectQuizAttemptsChart.destroy()
  subjectQuizAttemptsChart = new Chart(document.getElementById('subjectQuizAttemptsChart'), {
    type: 'bar',
    data: {
      labels: attemptsLabels,
      datasets: [{
        label: '',
        data: attemptsTotals,
        backgroundColor: '#4fd1c5',
      }]
    },
    options: {
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            precision: 0
          }
        }
      }
    }
  })

  // Monthly revenue chart
  const revenueRes = await axios.get('http://localhost:5000/api/admin/stats/monthly-revenue', { withCredentials: true })
  const revenueData = revenueRes.data
  const revenueLabels = revenueData.map(d => d.month)
  const revenueValues = revenueData.map(d => d.revenue)
  if (monthlyRevenueChart) monthlyRevenueChart.destroy()
  monthlyRevenueChart = new Chart(document.getElementById('monthlyRevenueChart'), {
    type: 'line',
    data: {
      labels: revenueLabels,
      datasets: [{
        label: '',
        data: revenueValues,
        borderColor: '#4fd1c5',
        backgroundColor: 'rgba(79,209,197,0.2)',
        fill: true
      }]
    },
    options: {
      plugins: {
        legend: { display: false }
      },
      scales: { y: { beginAtZero: true } }
    }
  })
})

onBeforeUnmount(() => {
  if (vantaEffect) vantaEffect.destroy();
})

function goBackToAdminDashboard() {
  router.push('/admin-dashboard')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
.dashboard-page-wrapper {
  min-height: 100vh;
  position: relative;
  background: transparent;
}
.vanta-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 0;
}
.stats-content {
  position: relative;
  z-index: 1;
  padding: 2rem;
  color: #fff;
  font-family: 'Orbitron', sans-serif;
}
.stats-header-row {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  justify-content: flex-start;
  gap: 2.5rem;
  margin-bottom: 2.5rem;
  width: 100%;
}
/* Heading box takes 35% width */
.stats-heading-box {
  flex: 0 0 35%;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
}
.dashboard-title {
  font-size: 7.5rem;
  padding: 0.5rem 0;
  color: #4fd1c5;
  font-family: 'Orbitron', sans-serif;
  margin-bottom: 0.7rem;
}
/* Summary row takes 65% width, cards are equal size and height */
.stats-summary-row {
  flex: 0 0 62.5%;
  display: flex;
  flex-direction: row;
  gap: 2rem;
  align-items: stretch;
  justify-content: flex-end;
  min-width: 420px;
}
/* Stat cards: equal width/height, increased height */
.stat-card {
  min-width: 200px;
  max-width: 260px;
  height: 170px;
  flex: 1 1 220px;
  padding: 2rem 1.2rem 1.2rem 1.2rem;
  margin-bottom: 0;
  border-radius: 1.2rem;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
}
.stat-title {
  color: #4fd1c5;
  font-size: 1.15rem;
  font-family: 'Orbitron', sans-serif;
  margin-bottom: 0.7rem;
}
.stat-value {
  font-size: 2.1rem;
  color: #fff;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
}
/* Charts row: cards equal size and gap */
.stats-charts-row {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  margin-top: 5.5rem;
  justify-content: center;
  align-items: stretch;
  width: 100%;
}
/* Chart cards: equal width/height */
.chart-card {
  min-width: 320px;
  max-width: 480px;
  width: 33%;
  height: 400px;
  flex: 1 1 400px;
  padding: 2rem 1.5rem 1.5rem 1.5rem;
  margin-bottom: 1rem;
  border-radius: 1.5rem;
  box-shadow: 0 0 16px 4px rgba(79,209,197,0.10);
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.glass-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}
.chart-title {
  color: #4fd1c5;
  font-size: 1.2rem;
  font-family: 'Orbitron', sans-serif;
  margin-bottom: 1.2rem;
  text-align: center;
}
.stats-card canvas {
  width: 100% !important;
  max-width: 420px;
  min-width: 320px;
  height: 320px !important;
  margin: 0 1rem;
  background: transparent;
}
.dashboard-footer {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 0 1rem 0;
  background: transparent;
}
.back-btn {
  font-size: 1.1rem;
  z-index: 100;
  padding: 0.7rem 2.2rem;
  border-radius: 1.2rem;
  background: #4fd1c5;
  color: #fff;
  border: none;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.17);
  cursor: pointer;
  transition: background 0.2s;
}
.back-btn:hover {
  background: #319795;
}
</style>
