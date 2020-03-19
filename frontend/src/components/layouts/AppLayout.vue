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
        <template v-for="(item, i) in menu_items">
          <v-list-group
            no-action
            v-if="item.submenu"
            :prepend-icon="item.icon"
          >
            <template v-slot:activator>
              <v-list-item-content>
                <v-list-item-title v-text="item.text"></v-list-item-title>
              </v-list-item-content>
            </template>
            <v-list-item
              v-for="(sb, i) in item.submenu"
              :key="i"
              :to="sb.to"
            >
              <v-list-item-content>
                <v-list-item-title v-text="sb.text" link :to="sb.to"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-group>

          <v-divider v-else-if="item.divider" :key="i"/>
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
      color="grey lighten-2"
      dense
    >
      <!-- -->
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <span class="title ml-3 mr-5 deep-orange--text">Patrowl&nbsp;<span class="font-weight-light deep">Hears</span></span>
      <v-text-field
        v-model="appsearch"
        solo-inverted
        flat
        hide-details
        label="Search"
        prepend-inner-icon="mdi-magnify"
        dense
        @keydown.enter="search()"
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

   <v-footer>
     <v-spacer></v-spacer>
    <div class="caption">&copy; {{ new Date().getFullYear() }} - Patrowl Hears - v0.0.4 (BETA)</div>
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
    appsearch: '',
    menu_items: [
      { icon: 'mdi-home', text: 'Home', to: '/homepage' },
      { divider: true },
      { icon: 'mdi-bookmark', text: 'KB', to: '', submenu: [
        { icon: 'mdi-bookmark', text: 'CVE', to: '/kb/cves' },
        { icon: 'mdi-bookmark', text: 'Bulletins', to: '/kb/bulletins' }
      ]},
      { icon: 'mdi-apps', text: 'Vendors & Products', to: '/products' },
      { icon: 'mdi-file-find', text: 'Vulnerabilities', to: '/vulns' },
      { icon: 'mdi-knife-military', text: 'Exploits', to: '/exploits' },
      { icon: 'mdi-security', text: 'Ratings', to: '/ratings' },
      { divider: true },
      // { heading: 'Labels' },
      { icon: 'mdi-toggle-switch', text: 'Settings', to: '/settings' },
      // { icon: 'mdi-help-circle', text: 'Help' },
    ],
    username: '',
  }),
  computed: {
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    },
  },
  mounted() {
    this.getUsername();
  },
  methods: {
    logout() {
      localStorage.removeItem('authToken');
      localStorage.removeItem('username');
      localStorage.removeItem('is_admin');
      localStorage.removeItem('is_org_admin');
      this.$router.push('/auth');
    },
    getUsername() {
      this.username = localStorage.getItem('username');
    },
    search() {
      // this.$router.go()
      if(this.$route.path === '/search/'+this.appsearch) {
        this.$router.go();
      } else {
        this.$router.push({ 'path': '/search/'+this.appsearch });
      }
    }
  }
}
</script>
