import Vue from 'vue'
import App from './App.vue'
import VueSession from 'vue-session'
import vuetify from './plugins/vuetify';
import router from './router'
import store from './store'

import axios from 'axios'
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
Vue.config.productionTip = false

new Vue({
  vuetify,
  router,
  VueSession,
  store,
  render: h => h(App)
}).$mount('#app')

var filter = function(text, length, clamp){
    clamp = clamp || '...';
    var node = document.createElement('div');
    node.innerHTML = text;
    var content = node.textContent;
    return content.length > length ? content.slice(0, length) + clamp : content;
};

Vue.filter('truncate', filter);

import moment from 'moment'
Vue.prototype.moment = moment
