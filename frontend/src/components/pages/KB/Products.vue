<template>
  <div>
    <!-- Products Page -->
    <!-- <div class="loading" v-if="loading===true">Loading&#8230;</div> -->
    <v-card>
      <v-card-title>
        <v-container>
          <v-row no-gutters >
            <v-col class="pa-2" md="auto">
                Products
            </v-col>
            <v-col class="pa-2">
              <v-chip
                small label outlined color="deep-orange"
                @click="toggleProductMonitored"
                v-if="this.only_monitored">Show all</v-chip>
              <v-chip
                small label outlined color="grey"
                @click="toggleProductMonitored"
                v-if="!this.only_monitored">Show monitored only</v-chip>
            </v-col>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
            ></v-text-field>
          </v-row>
        </v-container>
        <v-spacer></v-spacer>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="products.results"
        :options.sync="options"
        :server-items-length="products.count"
        :search="search"
        :footer-props="{
          'items-per-page-options': rowsPerPageItems
        }"
        :loading="loading"
        class="elevation-4"
        item-key="item"
        show-select
      >

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

        <!-- Updated at -->
        <template v-slot:item.updated_at="{ item }">
          <span>{{moment(item.updated_at).format('YYYY-MM-DD')}}</span>
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
  name: "products",
  data: () => ({
    products: [],
    loading: true,
    limit: 20,
    totalproducts: 0,
    only_monitored: false,
    search: '',
    options: {},
    selected: [],
    headers: [
      { text: 'Vendor', value: 'vendor' },
      { text: 'Product', value: 'name' },
      { text: 'Monitored', value: 'monitored', align: 'center', sortable: false },
      { text: 'Last update', value: 'updated_at' },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  mounted() {
    // this.getDataFromApi();
  },
  watch: {
    search: _.debounce(function (filter) {
      this.search = filter;
      this.options.page = 1;  // reset page count
      this.getDataFromApi();
    }, 500),
    only_monitored: {
      handler() {
        this.getDataFromApi();
      },
      deep: true
    },
    options: {
      handler() {
        this.getDataFromApi();
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
        // let search = this.search.trim().toLowerCase();
        this.limit = itemsPerPage;

        let items = this.getProducts(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            items
          });
        }, 300);
      });
      this.loading = false;
    },
    getProducts(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }
      let monitored = this.only_monitored ? "&is_monitored=true" : "";

      this.$api.get('/api/kb/products/?limit='+itemsPerPage+'&page='+page+'&search='+this.search+sorted_by+monitored).then(res => {
        this.loading = false;
        this.products = res.data;
        return this.products;
      }).catch(e => {
        this.products = [];
        swal.fire({
          title: 'Error',
          text: 'unable to get products',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
    },
    toggleMonitored(item) {
      // save in backend
      let data = {
        'vendor_name': item.vendor,
        'product_name': item.name,
        'monitored': !item.monitored
      };
      this.$api.post('/api/monitor/product/toggle', data).then(res => {
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
    toggleProductMonitored() {
      this.only_monitored = !this.only_monitored;
    }
  }
};
</script>
