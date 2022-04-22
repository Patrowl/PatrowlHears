
<template>
  <v-container grid-list-md>

    <v-snackbar v-model="snack" :timeout="snackTimeout" :color="snackColor">
      {{ snackText }}
      <v-btn text @click="snack = false">Close</v-btn>
    </v-snackbar>
  </v-container>
</template>

<script>

export default {
  name: 'AuthSSOLayout',
  data: () => ({
      snack: false,
      snackColor: '',
      snackText: '',
      snackTimeout: 3000,
  }),
  mounted() {
    // console.log(this.$route.query)

    if ("code" in this.$route.query){
      this.$api.get('/oauth2/callback').then((response) => {
        // console.log(response)
        this.$store.commit('updateToken', response.data.access);
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
      });
    } else {
      this.$api.get('/adfs/login-page').then((response) => {
        // console.log(response.data.url)
        // window.location.href = response.data.url
        window.location.href = decodeURI(response.data.url)
      });
    }
  },
}
</script>
<!-- http://web.patrowl-dev.io:8080/auth-sso?callback=2 -->
