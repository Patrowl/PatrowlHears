<template>
  <div>
    <!-- Vendor Page -->
    <div class="loading" v-if="loading===true">Loading&#8230;</div>
    <v-card>
      <v-card-title>
        Vendors
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="vendors.results"
        :options.sync="options"
        :server-items-length="vendors.count"
        :search="search"
        :footer-props="{
          'items-per-page-options': rowsPerPageItems
        }"
        :loading="loading"
        class="elevation-4"
        item-key="vendor"
        show-select
      >
      <!-- Actions -->
      <template v-slot:item.actions="{ item }">
        <v-icon
          small
          class="mdi mdi-eye"
          color="blue"
          @click="viewProducts(item.vendor)"
        >
        </v-icon>
        </v-icon>
      </template>

      <!-- Monitored -->
      <template v-slot:item.monitored="{ item }">
        <v-chip
          small label outlined color="deep-orange"
          @click="toggleMonitored(item)"
          v-if="item.monitored">Yes</v-chip>
        <v-chip
          small label outlined color="grey"
          @click="toggleMonitored(item)"
          v-if="!item.monitored">No</v-chip>
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

export default {
  name: "vendors",
  data: () => ({
    vendors: [],
    totalvendors: 0,
    loading: true,
    limit: 20,
    search: '',
    options: {},
    selected: [],
    headers: [
      { text: 'Vendor', value: 'vendor' },
      // { text: 'Monitored', value: 'monitored', align: 'center' },
      { text: 'Actions', value: 'actions' }

    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    // snack: false,
    // snackColor: '',
    // snackText: '',
  }),
  mounted() {
    // nothing yet
  },
  watch: {
    search: {
      handler(filter) {
        this.search = filter;
        this.options.page = 1;  // reset page count
        this.getDataFromApi().then(data => {
          // nothing
        });
      },
      deep: true
    },
    options: {
      handler() {
        this.getDataFromApi().then(data => {
          // nothing
        });
      },
      deep: true
    }
  },

  methods: {
    getDataFromApi() {
      this.loading = true;
      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options;
        let search = this.search.trim().toLowerCase();

        this.limit = itemsPerPage;
        let items = this.getvendors(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          this.loading = false;
          resolve({
            items
          });
        }, 300);
      });
    },
    getvendors(page, itemsPerPage, sortBy, sortDesc) {
      this.loading = true;
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }

      this.$api.get('/api/kb/vendors?limit='+itemsPerPage+'&page='+page+'&vendor__icontains='+this.search+'&'+sorted_by).then(res => {
        this.vendors = res.data;
        return this.vendors;
      }).catch(e => {
        this.vendors = [];
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get vendors',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
      this.loading = false;
    },
    viewProducts(vendor_name) {
      this.$router.push({ 'name': 'KBProductVersions', 'params': { 'vendor_name': vendor_name } });
    },
    // toggleMonitored(item) {
    //   // save in backend
    //   let data = {'monitored': !item.monitored};
    //   this.$api.put('/api/kb/vendor/'+item.id+'/', data).then(res => {
    //     if (res){
    //       item.monitored = !item.monitored;
    //       // Snack notifications
    //       this.snack = true;
    //       this.snackColor = 'success';
    //       this.snackText = 'Monitoring status successfuly updated.';
    //     } else {
    //       this.snack = true;
    //       this.snackColor = 'error';
    //       this.snackText = 'Unable to change the monitoring status';
    //     }
    //   }).catch(e => {
    //     this.loading = false;
    //     swal.fire({
    //       title: 'Error',
    //       text: 'Unable to change the monitoring status',
    //       showConfirmButton: false,
    //       showCloseButton: false,
    //       timer: 3000
    //     });
    //     return;
    //   });
    // },
  }
};
</script>
