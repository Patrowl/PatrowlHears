<template>
  <v-card>
    <v-card-title>
      <span class="headline">User information</span>
    </v-card-title>
    <v-card-text>
      <v-form ref="form-user">
        <v-container>
          <v-row>
            <v-col md="10">
              <v-text-field v-model="user_profile.username" label="Username" disabled></v-text-field>
              <v-text-field v-model="user_profile.first_name" label="Firstname" disabled></v-text-field>
              <v-text-field v-model="user_profile.last_name" label="Lastname" disabled></v-text-field>
              <v-text-field v-model="user_profile.email" label="email" disabled></v-text-field>
              <v-text-field v-model="moment(user_profile.last_login).format('YYYY-MM-DD, hh:mm:ss')" label="last_login" disabled></v-text-field>
            </v-col>
          </v-row>
          <v-btn color="deep-orange" @click="renewUserPassword">Renew password</v-btn> {{new_password}}
        </v-container>
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer></v-spacer>
    </v-card-actions>

    <v-snackbar v-model="snack" :timeout="3000" :color="snackColor" dense>
      {{ snackText }}
      <v-btn text @click="snack = false">Close</v-btn>
    </v-snackbar>
  </v-card>
</template>

<script>

export default {
  name: "UserEdit",
  props: ['user_id'],
  data: () => ({
    snack: false,
    snackColor: '',
    snackText: '',
    user_profile: {},
    user_profile_default: {
      username: '',
      email: '',
      last_login: '',
      first_name: '',
      last_name: '',
      orgs: [],
    },
    new_password: '',
  }),
  mounted() {
    this.loadUserProfile();
  },
  watch: {
    user_id: function(newVal, oldVal) {
      this.loadUserProfile();
    }
  },
  computed: {
  },
  methods: {
    loadUserProfile(){
      this.$api.get('/api/users/'+this.user_id).then(res => {
        if (res && res.status === 200) {
          this.user_profile = res.data;
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to retreive user\'s info';
      });
    },
    renewUserPassword(){
      this.$api.get('/api/users/profile/'+this.user_id+'/renewpassword').then(res => {
        if (res && res.status === 200 && res.data.status == "success") {
          this.new_password = 'New password: "'+res.data.password+'"';
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to retreive user\'s info';
      });
    }
  }
};
</script>

<style>
.v-dialog {
    position: absolute;
    left: 0;
}
</style>
