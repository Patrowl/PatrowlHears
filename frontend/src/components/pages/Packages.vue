<template>
  <div>
    <!-- Package -->
    <v-card>
      <v-card-title>
        <v-container>
          <v-row no-gutters >
            <v-col class="pa-2" md="auto">
                Packages
            </v-col>
            <v-col class="pa-2">
              <v-chip
                small label outlined color="deep-orange"
                @click="togglePackageMonitored"
                v-if="this.only_monitored_packages">Show all</v-chip>
              <v-chip
                small label outlined color="grey"
                @click="togglePackageMonitored"
                v-if="!this.only_monitored_packages">Show monitored only</v-chip>
            </v-col>
            <v-text-field
              v-model="search_packages"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
              class="pt-0"
            ></v-text-field>
          </v-row>
        </v-container>
        <v-spacer></v-spacer>
      </v-card-title>

      <v-data-table
        :headers="headers_packages"
        :items="packages.results"
        :options.sync="options_packages"
        :server-items-length="packages.count"
        :search="search_packages"
        :footer-props="{
          'items-per-page-options': rowsPerPageItems
        }"
        :loading="loading"
        :items-per-page="rowsPerPage"
        class="elevation-4"
      >

        <!-- Monitored -->
        <template v-slot:item.monitored="{ item }">
          <v-chip
            small label outlined color="deep-orange"
            @click="toggleMonitoredPackage(item)"
            v-if="item.monitored">Yes</v-chip>
          <v-chip
            small label outlined color="grey"
            @click="toggleMonitoredPackage(item)"
            v-if="!item.monitored">No</v-chip>
        </template>

        <!-- Updated at -->
        <template v-slot:item.updated_at="{ item }">
          <span>{{moment(item.updated_at).format('YYYY-MM-DD')}}</span>
        </template>

        <template v-slot:item.action="{ item }">
          <v-icon
            small
            class="mdi mdi-eye"
            color="blue"
            @click="viewPackage(item.id)"
          >
          </v-icon>
        </template>
      </v-data-table>

      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </v-card>
  </div>
</template>

<script>
import swal from 'sweetalert2';
import _ from 'lodash';

export default {
  name: "Packages",
  data: () => ({
    packages: [],
    loading: true,
    limit: 20,
    only_monitored_packages: false,
    search_packages: '',
    options_packages: {},
    headers_packages: [
      { text: 'Type', value: 'type' },
      { text: 'Package', value: 'name' },
      { text: 'Monitored', value: 'monitored', align: 'center', sortable: false },
      { text: 'Last update', value: 'updated_at' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    rowsPerPage: 10,
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  mounted() {
    // this.getDataProducts();
  },
  watch: {
    search_packages: _.debounce(function (filter) {
      this.search_packages = filter;
      this.options_packages.page = 1;  // reset page count
      this.getDataPackages();
    }, 500),
    only_monitored_packages: {
      handler() {
        this.getDataPackages();
      },
      deep: true
    },
    options_packages: {
      handler() {
        this.getDataPackages();
      },
      deep: true
    }
  },

  methods: {
    getDataPackages() {
      this.loading = true;
      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options_packages;
        // let search = this.search.trim().toLowerCase();
        this.limit = itemsPerPage;

        let items = this.getPackages(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            items
          });
        }, 300);
      });
      this.loading = false;
    },
    getPackages(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }
      let monitored = this.only_monitored_packages ? "&monitored=true" : "";

      this.$api.get('/api/kb/packages/?limit='+itemsPerPage+'&page='+page+'&name__icontains='+this.search_packages+sorted_by+monitored).then(res => {
        this.loading = false;
        this.packages = res.data;
        return this.packages;
      }).catch(e => {
        this.packages = [];
        swal.fire({
          title: 'Error',
          text: 'Unable to get packages',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
    },
    toggleMonitoredPackage(item) {
      // save in backend
      let data = {
        'package_id': item.id,
        'monitored': !item.monitored,
        'organization_id': localStorage.getItem('org_id')
      };
      this.$api.post('/api/monitor/package/toggle', data).then(res => {
        this.loading = false;
        if (res){
          item.monitored = !item.monitored;
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Monitoring status successfuly updated.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to change the monitoring status';
        }
      }).catch(e => {
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'Unable to change the monitoring status',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 2000
        });
        return;
      });
    },
    togglePackageMonitored() {
      this.only_monitored_packages = !this.only_monitored_packages;
      this.options_packages.page = 1;
    },
    viewPackage(package_id) {
      this.$router.push({ 'path': '/packages/'+package_id });
    },
  }
};
</script>
