import Vue from 'vue'
import App from './App.vue'
import vuetify from '@/plugins/vuetify'
import axios from 'axios'


Vue.config.productionTip = false
const axiosConfig = {
  baseURL: process.env.VUE_APP_BASE_PATH,
};
Vue.prototype.$axios = axios.create(axiosConfig)

new Vue({
  vuetify,
  render: h => h(App),
}).$mount('#app')
