import Vue from 'vue';
import App from './App.vue';
import VueSession from 'vue-session';
import vuetify from './plugins/vuetify';
import router from './router';
import store from './store';
import moment from 'moment';
import axios from 'axios';
import './common/filters';
import './common/scores';

import VuetifyConfirm from 'vuetify-confirm';
Vue.use(VuetifyConfirm, { vuetify });

Vue.use(VueSession);

// Axios
axios.interceptors.response.use(
  response => response,
  error => {
    const status = error.response;
  }
);

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
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

Vue.prototype.$api = axios;
Vue.prototype.moment = moment;
Vue.config.productionTip = false;

new Vue({
  vuetify,
  router,
  VueSession,
  store,
  render: h => h(App)
}).$mount('#app');

Vue.filter('capitalize', function (value) {
  if (!value) return ''
  value = value.toString()
  return value.charAt(0).toUpperCase() + value.slice(1)
});
