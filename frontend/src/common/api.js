import axios from 'axios'
import store from '../store'


const api = axios.create({
  baseURL: 'http://localhost:3333',
  headers: {}
});

api.defaults.timeout = 10000;
api.interceptors.request.use(
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

export default api
