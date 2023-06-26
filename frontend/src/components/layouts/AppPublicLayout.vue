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
      <img width="180px" src="../../assets/logo.png">
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
      <!-- <v-btn icon>
        <v-icon>mdi-bell</v-icon>
      </v-btn> -->
      <!-- <v-menu offset-y>
        <template v-slot:activator="{ on }">
          <v-btn
            tile
            v-on="on"
          >
            {{username}}@{{user_organization}}
          </v-btn>
        </template>
        <v-list>
          <v-list-item
            v-for="(item, index) in orgs"
            :key="index"
            @click="setOrganization(item)"
          >
            <v-list-item-title>{{ item.slug }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu> -->
      <v-btn href="/login">Login</v-btn>
      <v-btn icon href="/login"><v-icon>mdi-login</v-icon></v-btn>
    </v-app-bar>

    <!-- Sizes your content based upon application components -->
   <v-main>
     <!-- Provides the application the proper gutter -->
     <v-container fluid>
       <router-view></router-view>
     </v-container>
   </v-main>

   <v-footer>
     <v-spacer></v-spacer>
    <!-- <div class="caption">&copy; 2020-{{ new Date().getFullYear() }} - <v-chip color="deep-orange" label>Visit patrowl.io</v-chip> - {{app_version.version}} - {{app_version.edition|capitalize}} Edition {{app_version.build}}</div> -->
    <div class="caption"><v-chip color="deep-orange" href="https://canaris.in" small label>Visit Canaris</v-chip> - version {{app_version.version}} - {{app_version.edition|capitalize}} Edition {{app_version.build}}</div>
   </v-footer>
  </v-app>
</template>

<script>

import AppVersion from '../../../VERSION.json';
export default {
  name: 'AppPublicLayout',

  data: () => ({
    drawer: null,
    app_version: '',
    appsearch: '',
    menu_items: [
      { icon: 'mdi-home', text: 'Home', to: '/homepage' },
      { icon: 'mdi-magnify', text: 'Search', to: '/public/search' },
      { divider: true },
      { icon: 'mdi-file-multiple', text: 'Monitoring', to: '/monitoring' },
      { icon: 'mdi-file-find', text: 'Vulnerabilities', to: '/public/vulns' },
      { icon: 'mdi-knife-military', text: 'Exploits', to: '/exploits' },
      { icon: 'mdi-security', text: 'Ratings', to: '/ratings' },
      { icon: 'mdi-bookmark', text: 'CVE', to: '/kb/cves' },
      { icon: 'mdi-clipboard-check-outline', text: 'Bulletins', to: '/kb/bulletins' },
      { icon: 'mdi-apps', text: 'Vendors & Products', to: '/vendors' },
      { icon: 'mdi-package-variant', text: 'Packages', to: '/packages' },
      { divider: true },
      { icon: 'mdi-help-circle', text: 'Help', to: '/help' },
    ],
    username: '',
    user_organization: '',
    orgs: []
  }),

  mounted() {
    this.getUsername();
    this.getOrganization();
    this.getOrganizations();
    this.app_version = AppVersion;
  },
  methods: {
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
      this.$router.push('/auth');
    },
    getUsername() {
      this.username = localStorage.getItem('username');
    },
    getOrganization() {
      this.user_organization = localStorage.getItem('org_name');
    },
    getOrganizations() {
      this.orgs = JSON.parse(localStorage.getItem('orgs'));
    },
    search() {
      if(this.$route.path === '/public/search/'+this.appsearch) {
        this.$router.go();
      } else {
        this.$router.push({ 'path': '/public/search/'+this.appsearch });
      }
    },
    setOrganization(org){
      this.$api.get('/users/set-org/'+org.id).then(res => {
        if (res && res.status === 200 && res.data.status === "set") {
          localStorage.setItem('org_id', org.id);
          localStorage.setItem('org_name', org.name);
          this.user_organization = org.name;
          this.$router.go();
        }
      });
    }
  }
}
</script>
