<template>
  <div class="page-wrapper">
    <div ref="vantaBg" class="vanta-bg"></div>
    <div class="content-wrapper">
      <div class="intro-text">INTRODUCING</div>
      <div class="content-main animate">
        <div class="container">
          <h1 class="headline">QUIZ MASTER</h1>
          <h2 class="subheadline">PRACTICE. PROGRESS. PREVAIL.</h2>
        </div>
      </div>
    </div>
    <div class="button-blur-container">
      <button class="nav-btn" title="Login" @click="navigateTo('/login')">LOGIN</button>
      <button class="nav-btn" title="Register" @click="navigateTo('/register')">REGISTER</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      vantaEffect: null
    }
  },
  methods: {
    navigateTo(route) {
      this.$router.push(route);
    }
  },
  mounted() {
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
          backgroundColor: 0x0f111a, // Deep dark Windows UI tone
          color: 0x4fd1c5,           // Cyan-teal for modern highlight
          spacing: 40,               // Tight spacing for denser mesh
          points: 12,                // More points = finer network
          maxDistance: 25           // Tighter links = smooth motion
        });
      } else {
        setTimeout(tryInit, 100);
      }
    };
    tryInit();
  },
  beforeUnmount() {
    if (this.vantaEffect) this.vantaEffect.destroy();
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

/* Removed Navbar and Footer styles */

/* Global styles */
html, body {
  height: 100%;
  margin: 0;
  font-family: 'Montserrat', sans-serif;
  scrollbar-width: none;        /* Firefox */
  -ms-overflow-style: none;     /* IE/Edge */
  overflow: auto;
}

html::-webkit-scrollbar,
body::-webkit-scrollbar {
  display: none;                /* Chrome, Safari */
}

.page-wrapper {
  width: 100%;
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

.content-wrapper {
  display: block;
  height: 100%;
  width: 100%;
  position: absolute;
  z-index: 1;
}

.content-main {
  display: block;
  position: relative;
  width: 100vw;
  height: 100vh;
}

.container {
  position: static;
  z-index: 2;
}

.headline {
  font-family: 'Megum', 'Montserrat', sans-serif;
  font-size: 9rem;
  font-weight: normal;
  color: #fff;
  margin-bottom: 2rem;
  text-align: center;
  letter-spacing: 0.08em;
  line-height: 1.1;
  position: absolute;
  top: 45%; /* shifted above */
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  width: max-content;
  background: none;
}

.subheadline {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.2rem;
  color: #d6e0df;
  text-align: center;
  margin-top: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-shadow: 0 2px 16px rgba(79,209,197,0.18);
  position: absolute;
  top: calc(40% + 5.5rem); /* keep below headline */
  left: 50%;
  transform: translate(-50%, 0);
  z-index: 10;
  width: max-content;
}

/* Button styles */
.button-blur-container {
  position: fixed;
  bottom: 9.5rem;
  left: 0;
  width: 100vw;
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  z-index: 100;
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
  width: 220px;
  min-width: 220px;
  max-width: 220px;
}
.nav-btn:hover {
  background: rgba(79, 209, 197, 0.18); /* #4fd1c5 with alpha */
  color: #4fd1c5;
  box-shadow: 0 0 32px 8px rgba(79,209,197,0.18) inset, 0 0 16px 4px rgba(79,209,197,0.10);
}

.intro-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.2rem;
  letter-spacing: 0.25em;
  color: #4fd1c5;
  text-align: center;
  margin-top: 2.5rem;
  margin-bottom: 1.5rem;
  font-weight: 700;
  text-shadow: 0 2px 16px rgba(79,209,197,0.18);
  z-index: 100;
  position: absolute;
  left: 50%;
  top: 2.5rem;
  transform: translateX(-50%);
  width: max-content;
  display: block;
}
</style>