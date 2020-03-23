<template>
    <div>
      Settings Page (Admin only)
      <v-tabs
        left
        background-color="white"
        color="deep-orange accent-4"
      >
        <v-tab v-if="isAdmin() == 'true'">Sync</v-tab>
        <v-tab v-if="isOrgAdmin() == 'true'">Orgs & Users</v-tab>

        <!-- Sync -->
        <v-tab-item v-if="isAdmin() == 'true'">
          <v-row>
            <v-col cols="3">
              <v-card
              class="mx-auto"
              >
                <v-list dense>
                  <v-subheader>Synchronize data (admin only)</v-subheader>
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
        </v-tab-item>

        <!-- Orgs & Users -->
        <v-tab-item>

          <!-- Organizations -->
          <v-card>
            <v-card-title>
              Organizations
            </v-card-title>
            <v-data-table
              :headers="orgs_headers"
              :items="orgs.results"
              :options.sync="orgs_options"
              :server-items-length="orgs.count"
              :items-per-page="5"
              :footer-props="{
                'items-per-page-options': rowsPerPageItems
              }"
              :loading="loading"
              class="elevation-4"
              item-key="id"
              show-select
              multi-sort
            >
              <template v-slot:item.action="{ item }">
                <v-icon
                  small
                  class="mdi mdi-account-plus"
                  color="green"
                  @click="openInvitationDialog(item.id, item.name)"
                >
                </v-icon>
              </template>
            </v-data-table>

            <v-dialog v-model="dialog_invitation" max-width="500px">
              <!-- <template v-slot:activator="{ on }">
                <v-btn absolute dark fab bottom left color="deep-orange" v-on="on">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </template> -->
              <v-card>
                <v-card-title>
                  Invite people to organzation '{{invitation.org_name}}'
                  <!-- <span class="headline">{{ formExploitTitle }}</span> -->
                </v-card-title>
                <v-card-text>
                  <v-container>
                    <v-form ref="form-user-invitation">
                      <v-text-field
                        v-model="invitation.email"
                        label="Email"
                        :rules="emailRules"
                        required></v-text-field>
                      <v-checkbox
                        v-model="invitation.is_admin"
                        label="Is admin ?"></v-checkbox>

                      <v-btn color="success" @click="addUserToOrg" small>Invite</v-btn>
                      <v-btn color="warning" type="reset" small>Reset</v-btn>
                      <!-- <v-btn color="primary" small>Cancel</v-btn> -->
                    </v-form>
                  </v-container>
                </v-card-text>

                <v-card-actions>
                  <v-spacer></v-spacer>
                  <!-- <v-btn color="blue darken-1" text @click="close">Cancel</v-btn> -->
                  <!-- <v-btn color="blue darken-1" text @click="save">Save</v-btn> -->
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-card>
          <br/>
          <!-- Users -->
          <v-card>
            <v-card-title>
              Users
            </v-card-title>
            <v-data-table
              :headers="users_headers"
              :items="users.results"
              :options.sync="users_options"
              :server-items-length="users.count"
              :items-per-page="20"
              :footer-props="{
                'items-per-page-options': rowsPerPageItems
              }"
              :loading="loading"
              class="elevation-4"
              item-key="id"
              show-select
              multi-sort
            >
              <template v-slot:item.is_admin="{ item }">
                <v-icon
                  small
                  class="mdi mdi-shield-check"
                  color="deep-orange"
                  v-if="item.is_admin == true"
                >
                </v-icon>
              </template>
              <template v-slot:item.action="{ item }">
                <!-- <v-icon
                  small
                  class="mdi mdi-account-cancel"
                  color="orange"
                  @click="disableUserFromOrg(item.id)"
                >
                </v-icon> -->
                <v-icon
                  small
                  class="mdi mdi-account-remove"
                  color="red"
                  @click="delUserFromOrg(item.org_id, item.user, item)"
                >
                </v-icon>
              </template>
            </v-data-table>
          </v-card>
        </v-tab-item>
      </v-tabs>
      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </div>
</template>

<script>
import router from "../../router";
import Users from "../../common/users";

export default {
  name: "Settings",
  mixins: [Users],
  data: () => ({
    loading: true,
    async_item: 1,
    async_items: [
      { text: 'CWE', icon: 'mdi-clock', to: '/api/kb/cwes/async' },
      { text: 'CPE', icon: 'mdi-clock', to: '/api/kb/cpes/async' },
      { text: 'Bulletins', icon: 'mdi-clock', to: '/api/kb/bulletins/async' },
      { text: 'CVE', icon: 'mdi-clock', to: '/api/kb/cves/async' },
      { text: 'VIA', icon: 'mdi-clock', to: '/api/kb/vias/async' },
    ],
    orgs: [],
    orgs_options: {},
    org_selected: '',
    orgs_headers: [
      { text: 'Organization Name', value: 'name' },
      { text: 'Actions', value: 'action', align: 'center', sortable: false },
    ],
    // search_orgs: '',
    users: [],
    users_options: {},
    users_headers: [
      { text: 'Organization name', value: 'org_name' },
      { text: 'Username', value: 'username' },
      { text: 'Email', value: 'email' },
      { text: 'Admin ?', value: 'is_admin' },
      { text: 'Actions', value: 'action', align: 'center', sortable: false },
    ],
    invitation: {
      org_name: '',
      org_id: 0,
      email: '',
      is_admin: false
    },
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
    ],
    // search_users: '',
    rowsPerPageItems: [5, 10, 20, 50, 100],
    dialog_invitation: false,
    snack: false,
    snackColor: '',
    snackText: ''
  }),
  mounted() {
  },
  watch: {
    orgs_options: {
      handler() {
        this.getDataFromApiOrgs().then(data => {
        });
      },
      deep: true
    },
    users_options: {
      handler() {
        this.getDataFromApiUsers().then(data => {
        });
      },
      deep: true
    },
  },
  methods: {
    getDataFromApiOrgs() {
      this.loading = true;

      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.orgs_options;

        this.limit = itemsPerPage;
        let orgs = this.getOrgs(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            orgs
          });
        }, 300);
        this.loading = false;
      });
      this.loading = false;
    },
    getDataFromApiUsers() {
      this.loading = true;

      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.users_options;

        this.limit = itemsPerPage;
        let users = this.getUsers(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            users
          });
        }, 300);
        this.loading = false;
      });
      this.loading = false;
    },
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
      }).catch(e => {
        swal.fire({
          title: 'Error',
          text: 'Unable to call action',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    getOrgs(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }
      this.$api.get('/api/orgs/?limit='+itemsPerPage+'&page='+page+sorted_by).then(res => {
        if (res && res.status === 200) {
          this.orgs = res.data;
        }
      }).catch(e => {
        this.orgs = [];
        swal.fire({
          title: 'Error',
          text: 'Unable to get org users',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    getUsers(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }
      this.$api.get('/api/users/?limit='+itemsPerPage+'&page='+page+'&'+sorted_by).then(res => {
        if (res && res.status === 200) {
          this.users = res.data;
        }
      }).catch(e => {
        this.users = [];
        swal.fire({
          title: 'Error',
          text: 'Unable to get org users',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    openInvitationDialog(org_id, org_name) {
      this.invitation.org_id = org_id
      this.invitation.org_name = org_name
      this.dialog_invitation = true;
    },
    addUserToOrg(org_id) {
      this.dialog_invitation = false;
      var bodyFormData = new FormData();
      bodyFormData.set('email', this.invitation.email);
      bodyFormData.set('is_admin', this.invitation.is_admin);
      // this.$api.post('/users/'+this.invitation.org_id+'/add', bodyFormData).then(res => {
      this.$api.post('/users/'+this.invitation.org_id+'/adduser', bodyFormData).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Invitation successfuly sent.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'An error occured during the invitation.';
        }

      }).catch(e => {
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to save related exploits',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    async delUserFromOrg(org_id, user_id, item) {
      let confirm = await this.$confirm('Do you really want to delete user ?', { title: 'Warning' });
      if (confirm) {
        this.$api.get('/users/'+org_id+'/delete/'+user_id).then(res => {
          if (res && res.status === 200) {
            let idx = this.users.results.indexOf(item);
            this.users.results.splice(idx, 1);
          }
        });
      }
    },
  }
};
</script>
