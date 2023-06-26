<template>
  <v-container grid-list-md>
    <v-layout row wrap align-center justify-center fill-height>
      <v-flex xs12 sm8 lg4 md5>
        <v-card class="registration-card">
          <v-card-title>
            <span class="headline">Register to CanPatch</span>
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
                  v-model="registration.email"
                  label="Email"
                  :rules="rules.email"
                  required
                  disabled
                />

                <v-text-field
                  v-model="registration.username"
                  :counter="128"
                  label="Username"
                  maxlength="128"
                  required
                  autocomplete="username"
                />

                <v-text-field
                  type="password"
                  v-model="registration.password"
                  :rules="rules.password"
                  :counter="30"
                  label="Password"
                  maxlength="30"
                  required
                  autocomplete="new-password"
                />

                <v-text-field
                  type="password"
                  v-model="registration.password_confirm"
                  :rules="rules.password"
                  :counter="30"
                  label="Password (again)"
                  maxlength="30"
                  required
                  autocomplete="new-password"
                />

                <v-text-field
                  v-model="registration.first_name"
                  :counter="128"
                  label="Firstname"
                  maxlength="128"
                  autocomplete="firstname"
                />

                <v-text-field
                  v-model="registration.last_name"
                  :counter="128"
                  label="Lastname"
                  maxlength="128"
                  autocomplete="lastname"
                  @keyup.enter.native="register"
                />

              </v-container>
              <v-btn class="deep-orange white--text" :disabled="!valid" @click="register">Register</v-btn>

            </v-form>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import router from "../../router";
export default {
  name: "UserRegistrationLayout",
  data: () => ({
    loading: false,
    valid: true,
    registration: {
      email: '',
      username: '',
      password: '',
      password_confirm: '',
      first_name: '',
      last_name: ''
    },
    rules: {
      username: [
        v => !!v || "Username is required",
        v => (v && v.length > 3) || "A username must be more than 3 characters long",
        v => /^[a-z0-9_]+$/.test(v) || "A username can only contain letters and digits"
      ],
      password: [
        v => !!v || "Password is required",
        v => (v && v.length > 8) || "The password must be longer than 8 characters",
        v => /(?=.*[A-Z])/.test(v) || 'Must have one uppercase character',
        v => /(?=.*\d)/.test(v) || 'Must have one number',
        v => /([!@#$%-_])/.test(v) || 'Must have one special character [!@#$%-_]'
      ],
      email: [
        v => !!v || 'E-mail is required',
        v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
      ],
    },
  }),
  beforeRouteUpdate(to) {
    this.invitation_token = to.query.token;
    this.checkToken();
  },
  mounted() {
    this.invitation_token = this.$router.currentRoute.query.token;
    this.checkToken();
  },
  methods: {
    checkToken() {
      this.$api.get('/users/activate/'+this.invitation_token).then(res => {
        if (res && res.status === 200 && res.data.status === "valid") {
          this.registration.email = res.data.email;
        } else {
          this.$router.push('/auth');
        }
      }).catch(e => {
        this.$router.push('/auth');
      });

    },
    register() {
      this.$api.post('/users/activate/'+this.invitation_token, this.registration).then(res => {
        if (res && res.status === 200 && res.data.status === "success") {
          this.$router.push('/auth');
        }
      }).catch(e => {
        //todo
      });
    }
  }
};
</script>
