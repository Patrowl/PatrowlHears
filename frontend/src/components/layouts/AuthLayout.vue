
<template>
  <v-container grid-list-md>
    <v-layout row wrap align-center justify-center fill-height>
      <v-flex xs12 sm8 lg4 md5>
        <v-card class="login-card">
          <v-card-title>
            <span class="headline">Login to CanPatch</span>
          </v-card-title>

          <v-spacer/>

          <v-card-text>
            <v-layout
              row
              fill-height
              justify-center
              align-center
              v-if="loading"
            >
              <v-progress-circular
                :size="50"
                color="primary"
                indeterminate
              />
            </v-layout>

            <v-form v-else ref="form" v-model="valid" lazy-validation>
              <v-container>

                <v-text-field
                  v-model="credentials.username"
                  :counter="70"
                  label="username"
                  maxlength="70"
                  autocomplete="username"
                  required
                />
                <v-text-field
                  type="password"
                  v-model="credentials.password"
                  :counter="256"
                  label="password"
                  :rules="rules.password"
                  maxlength="256"
                  autocomplete="current-password"
                  required
                  @keyup.enter.native="login"
                />
                <v-checkbox
                  v-model="credentials.enable_firststeps"
                  label="First visit"
                />

                <!-- <v-checkbox
                  v-model="credentials.use_default_organization"
                  label="Use default Organization"
                  disabled
                /> -->

              </v-container>
              <v-btn class="deep-orange white--text" :disabled="!valid" @click="login" block>Login</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
        <br/>
        <!-- <v-card class="saas-card" color="deep-orange" center="center">
          <v-card-actions>
              <v-btn text block @click="loginsso">
                SSO + 2FA Authentication
              </v-btn>
            </v-card-actions>
        </v-card> -->
      </v-flex>
    </v-layout>
    <v-snackbar v-model="snack" :timeout="snackTimeout" :color="snackColor">
      {{ snackText }}
      <v-btn text @click="snack = false">Close</v-btn>
    </v-snackbar>
  </v-container>
</template>

<script>
import swal from 'sweetalert2';

export default {
  name: 'AuthLayout',
  data: () => ({
      credentials: {
        'username': '',
        'password': '',
        'use_default_organization': true,
        'enable_firststeps': true
      },
      valid:true,
      loading:false,
      rules: {
        username: [
          v => !!v || "Username is required",
          v => (v && v.length > 3) || "A username must be more than 3 characters long",
          v => /^[a-z0-9_]+$/.test(v) || "A username can only contain letters and digits"
        ],
        password: [
          v => !!v || "Password is required",
          v => (v && v.length < 256) || "The password must be lesser than 256 characters"
        ]
      },
      snack: false,
      snackColor: '',
      snackText: '',
      snackTimeout: 3000,
  }),

  methods: {
    login() {
      // checking if the input is valid
      if (this.$refs.form.validate()) {
        this.loading = true;
        this.$store.commit("removeToken");
        this.$api.post(this.$store.state.endpoints.obtainJWT, this.credentials).then(res => {
          this.$store.commit('updateToken', res.data.access);
          // console.log(this.$store.state)

          // set default organization
          let org_name = "";
          this.$api.get('/users/set-org').then(res => {
            if (res && res.status === 200 && res.data.status === "set") {
              // this.$session.set('org_id', res.data.org_id);
              // this.$session.set('org_name', res.data.org_name);
              localStorage.setItem('org_id', res.data.org_id);
              localStorage.setItem('org_name', res.data.org_name);

              // get and set auth user
              this.$api.get("/users/api/current").then((response) => {
                localStorage.setItem('username', response.data.username);
                localStorage.setItem('is_admin', response.data.is_superuser);
                localStorage.setItem('is_org_admin', response.data.is_org_admin);
                // localStorage.setItem('org_id', response.data.current_org.org_id);
                localStorage.setItem('orgs', JSON.stringify(response.data.orgs));
                localStorage.setItem('org_name', response.data.current_org.org_name);
                localStorage.setItem('profile', JSON.stringify(response.data.profile));
                // response.data['org_name'] = org_name;
                if (response.data.is_superuser == true) {
                  localStorage.setItem('is_org_admin', true);
                }
                this.$store.commit("setAuthUser",
                  {authUser: response.data, isAuthenticated: true}
                );
                if (this.credentials.enable_firststeps == true) {
                  this.$router.push({name: 'Homepage', query: { firststeps: '1' }});
                } else {
                  this.$router.push({name: 'Homepage'});
                }
              });
            } else {
              this.logout();
              this.loading = false;
              this.snack = true;
              this.snackColor = 'error';
              this.snackText = 'Unable to set organization';
            }
          });
        }).catch(e => {
          this.$store.commit("removeToken");
          this.loading = false;
          swal.fire({
            title: 'Error',
            text: 'Wrong username or password',
            showConfirmButton:false,
            showCloseButton:false,
            timer:3000
          });
        });
      }
    },
    loginsso() {
      this.$router.push({name: 'AuthSSOLayout'});
    },
    logout() {
      this.$store.commit("removeToken");
      localStorage.removeItem('authToken');
      localStorage.removeItem('username');
      localStorage.removeItem('is_admin');
      localStorage.removeItem('is_org_admin');
      localStorage.removeItem('orgs');
      localStorage.removeItem('org_id');
      localStorage.removeItem('org_name');
      this.$session.destroy();
    },
  }
}
</script>
