import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
// Font Awesome setup
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faEye, faEyeSlash, faAnglesLeft, faBook, faClipboardList, faChartBar, faUserGraduate, faSearch, faUser, faRightFromBracket, faHome, faTrophy, faXmark, faUsers } from '@fortawesome/free-solid-svg-icons'
import { tryAutoLogin } from './stores/user.js'

library.add(faEye, faEyeSlash, faAnglesLeft, faBook, faClipboardList, faChartBar, faUserGraduate, faSearch, faUser, faRightFromBracket, faHome, faTrophy, faXmark, faUsers)

// Initialize user store
tryAutoLogin()

const app = createApp(App);
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router);
app.mount('#app');