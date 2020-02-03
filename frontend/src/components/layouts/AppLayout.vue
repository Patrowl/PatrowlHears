<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      clipped
      app
      color="grey lighten-4"
    >
      <!-- -->
      <v-list dense class="grey lighten-4">
        <template v-for="(item, i) in menu_items" :to="item.to">
          <v-row
            v-if="item.heading"
            :key="i"
            align="center"
          >
            <v-col cols="6">
              <v-subheader v-if="item.heading">
                {{ item.heading }}
              </v-subheader>
            </v-col>
            <!-- <v-col cols="6" class="text-right">
              <v-btn small text>edit</v-btn>
            </v-col> -->
          </v-row>
          <v-divider
            v-else-if="item.divider"
            :key="i"
            dark
            class="my-4"
          />
          <v-list-item v-else :key="i" link :to="item.to">
            <v-list-item-action>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title class="grey-darken-3--text">
                {{ item.text }}
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>

        </template>
      </v-list>


    </v-navigation-drawer>

    <v-app-bar
      app
      clipped-left
      color="light-blue accent-4"
      dense
    >
      <!-- -->
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <span class="title ml-3 mr-5">Patrowl&nbsp;<span class="font-weight-light">Hears</span></span>
      <v-text-field
        solo-inverted
        flat
        hide-details
        label="Search"
        prepend-inner-icon="mdi-magnify"
        dense
      />

      <v-spacer />
      <v-btn icon>
        <v-icon>mdi-bell</v-icon>
      </v-btn>
      {{username}}
      <v-btn icon @click="logout"><v-icon>mdi-logout</v-icon></v-btn>
    </v-app-bar>

    <!-- Sizes your content based upon application components -->
   <v-content>
     <!-- Provides the application the proper gutter -->
     <v-container fluid>
       <router-view></router-view>
     </v-container>
   </v-content>

   <v-footer app>
     <!-- -->
   </v-footer>
  </v-app>
</template>

<script>
export default {
  name: 'AppLayout',
  // props: {
  //   source: String,
  // },
  data: () => ({
    drawer: null,
    menu_items: [
      { heading: 'KB' },
      { icon: 'mdi-bookmark', text: 'Vendors', to: '/kb/vendors' },
      { icon: 'mdi-bookmark', text: 'CVE', to: '/kb/cves' },
      { icon: 'mdi-bookmark', text: 'Bulletins', to: '/kb/bulletins' },
      { divider: true },
      { icon: 'mdi-file-find', text: 'Vulnerabilities', to: '/vulns' },
      { icon: 'mdi-security', text: 'Ratings', to: '/ratings' },
      { icon: 'mdi-cctv', text: 'Monitoring', to: '/monitoring' },
      { icon: 'mdi-alert', text: 'Alerts', to: '/alerts' },
      { icon: 'mdi-file-chart', text: 'Reports', to: '/reports' },
      { divider: true },
      // { heading: 'Labels' },
      { icon: 'mdi-settings', text: 'Settings' },
      { icon: 'mdi-help-circle', text: 'Help' },
    ],
    username: ''
  }),
  computed: {
    isAuthenticated() {
      // return true;
      return this.$store.getters.isAuthenticated;
    }
  },
  mounted() {
    this.getUsername();
  },
  methods: {
    logout() {
      localStorage.removeItem('authToken');
      localStorage.removeItem('username');
      this.$router.push('/auth');
    },
    getUsername() {
      this.username = this.$store.state.authUser.username;
    }
  }
}
</script>
