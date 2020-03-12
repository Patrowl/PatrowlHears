
<template>
  <v-container grid-list-md>
    <v-layout row wrap align-center justify-center fill-height>
      <v-flex xs12 sm8 lg4 md5>
        <v-card class="login-card">
          <v-card-title>
            <span class="headline">Login to PatrowlHears</span>
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
                  required
                />

                <v-text-field
                  type="password"
                  v-model="credentials.password"
                  :counter="20"
                  label="password"
                  :rules="rules.password"
                  maxlength="20"
                  required
                />

              </v-container>
              <v-btn class="deep-orange white--text" :disabled="!valid" @click="login">Login</v-btn>

            </v-form>


          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import axios from 'axios';
import swal from 'sweetalert2';

export default {
  name: 'AuthLayout',
  data: () => ({
      credentials: {},
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
          v => (v && v.length > 7) || "The password must be longer than 7 characters"
        ]
      }
  }),

  methods: {
    login() {
      // checking if the input is valid
      if (this.$refs.form.validate()) {
        this.loading = true;
        this.$store.commit("removeToken");
        this.$api.post(this.$store.state.endpoints.obtainJWT, this.credentials).then(res => {
          this.$store.commit('updateToken', res.data.access);

          // get and set auth user
          this.$api.get("/users/api/current").then((response) => {
            this.$store.commit("setAuthUser",
              {authUser: response.data, isAuthenticated: true}
            );
            this.$router.push({name: 'Homepage'});
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
    }
  }
}
</script>
