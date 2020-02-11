import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import VueAxios from 'vue-axios'
import jwt_decode from 'jwt-decode'

// axios.defaults.xsrfCookieName = 'csrftoken'
// axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.baseURL = process.env.VUE_APP_API_BASE_URL || process.env.API_BASE_URL || 'http://localhost:3333/'

Vue.use(Vuex)
Vue.use(VueAxios, axios);

export default new Vuex.Store({
  state: {
    authUser: {},
    // status: '',
    isAuthenticated: false,
    jwt_auth_token: localStorage.getItem('authToken'),
    jwt_refresh_token: localStorage.getItem('refreshToken'),
    endpoints: {
      obtainJWT: '/auth-jwt/obtain_jwt_token/',
      refreshJWT: '/auth-jwt/refresh_jwt_token/'
    }
  },
  getters: {
    isLoggedIn (state) {
      return state.jwt_auth_token != null
    }
  },
  mutations: {
    setAuthUser(state, {
      authUser,
      isAuthenticated
    }) {
      Vue.set(state, 'authUser', authUser);
      Vue.set(state, 'isAuthenticated', isAuthenticated);
    },
    updateToken(state, newToken){
      localStorage.setItem('authToken', newToken);
      state.jwt_auth_token = newToken;
    },
    removeToken(state){
      localStorage.removeItem('authToken');
      state.jwt_auth_token = null;
    }
  },
  actions: {
    obtainToken(username, password){
      const payload = {
        username: username,
        password: password
      }
      // axios.post(this.state.endpoints.obtainJWT, payload)
      this.$api.post(this.state.endpoints.obtainJWT, payload)
        .then((response)=>{
            this.commit('updateToken', response.data.access);
          })
        .catch((error)=>{
            console.log(error);
          })
    },
    refreshToken(){
      const payload = {
        token: this.state.jwt_refresh_token
      }
      // axios.post(this.state.endpoints.refreshJWT, payload)
      this.$api.post(this.state.endpoints.refreshJWT, payload)
        .then((response)=>{
            this.commit('updateToken', response.data.access)
          })
        .catch((error)=>{
            console.log(error)
          })
    },
    inspectToken(){
      const token = this.state.jwt_auth_token;
      if(token){
        const decoded = jwt_decode(token);
        const exp = decoded.exp
        const orig_iat = decode.orig_iat
        if(exp - (Date.now()/1000) < 1800 && (Date.now()/1000) - orig_iat < 628200){
          this.dispatch('refreshToken')
        } else if (exp -(Date.now()/1000) < 1800){
          // DO NOTHING, DO NOT REFRESH
        } else {
          // PROMPT USER TO RE-LOGIN, THIS ELSE CLAUSE COVERS THE CONDITION WHERE A TOKEN IS EXPIRED AS WELL
        }
      }
    }
  },
  modules: {
  }
})
