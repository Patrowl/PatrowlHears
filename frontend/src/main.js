import Vue from 'vue'
import App from './App.vue'
import VueSession from 'vue-session'
import VueDragDrop from 'vue-drag-drop';
import vuetify from './plugins/vuetify';
import router from './router'
import store from './store'
import moment from 'moment'
import axios from 'axios'
import './common/filters'

// Axios
axios.interceptors.response.use(
  response => response,
  error => {
    const status = error.response;
  }
)

axios.interceptors.request.use(
  config => {
    if (store.state.jwt_auth_token) {
      config.headers.Authorization = 'JWT '+store.state.jwt_auth_token
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);
Vue.prototype.$api = axios
Vue.prototype.moment = moment
Vue.config.productionTip = false

new Vue({
  vuetify,
  router,
  VueSession,
  store,
  render: h => h(App)
}).$mount('#app')

// var filter = function(text, length, clamp){
//     clamp = clamp || '...';
//     var node = document.createElement('div');
//     node.innerHTML = text;
//     var content = node.textContent;
//     return content.length > length ? content.slice(0, length) + clamp : content;
// };
//
// Vue.filter('truncate', filter);
Vue.filter('capitalize', function (value) {
  if (!value) return ''
  value = value.toString()
  return value.charAt(0).toUpperCase() + value.slice(1)
});

Vue.use(VueDragDrop);
