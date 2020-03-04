<template>
    <div>
      Settings Page
      <v-row>
        <v-col cols="3">
          <v-card
          class="mx-auto"
          >
            <v-list dense>
              <v-subheader>Synchronize data</v-subheader>
              <v-list-item-group v-model="async_item" color="primary">
                <v-list-item
                  v-for="(async_item, i) in async_items"
                  :key="i"
                  @click="callAction(async_item)"
                >
                  <v-list-item-icon>
                    <v-icon v-text="async_item.icon" color="deep-orange">
                    </v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      v-text="async_item.text"
                      link
                      :to="async_item.to">
                    </v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </div>
</template>

<script>
import router from "../../router";
export default {
  name: "Settings",
  data: () => ({
    // sync_item: 1,
    // sync_items: [
    //   { text: 'CWE', icon: 'mdi-flag', to: '/api/kb/cwes/sync' },
    //   { text: 'CPE', icon: 'mdi-flag', to: '/api/kb/cpes/sync' },
    //   { text: 'Bulletins', icon: 'mdi-flag', to: '/api/kb/bulletins/sync' },
    //   { text: 'CVE', icon: 'mdi-flag', to: '/api/kb/cves/sync' },
    //   { text: 'VIA', icon: 'mdi-flag', to: '/api/kb/vias/sync' },
    // ],
    async_item: 1,
    async_items: [
      { text: 'CWE', icon: 'mdi-clock', to: '/api/kb/cwes/async' },
      { text: 'CPE', icon: 'mdi-clock', to: '/api/kb/cpes/async' },
      { text: 'Bulletins', icon: 'mdi-clock', to: '/api/kb/bulletins/async' },
      { text: 'CVE', icon: 'mdi-clock', to: '/api/kb/cves/async' },
      { text: 'VIA', icon: 'mdi-clock', to: '/api/kb/vias/async' },
    ],
    snack: false,
    snackColor: '',
    snackText: ''
  }),
  mounted() {
    // this.checkLoggedIn();
  },
  methods: {
    callAction(item) {
      this.$api.get(item.to).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Sync successfuly enqueued.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to sync :/';
        }
        //this.vuln = res.data;
      }).catch(e => {
        swal.fire({
          title: 'Error',
          text: 'Unable to call action',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    }
    // checkLoggedIn() {
    //   this.$session.start();
    //   if (!this.$session.has("token")) {
    //     router.push("/auth");
    //   }
    // }
  }
};
</script>
