<template>
  <div>
    <!-- Products Page -->
    <!-- <div class="loading" v-if="loading===true">Loading&#8230;</div> -->
    <v-tabs
      left
      background-color="white"
      color="deep-orange accent-4"
    >
      <v-tab>By Vendors</v-tab>
      <v-tab>By Products</v-tab>

      <!-- Vendors -->
      <v-tab-item>
        <v-card>
          <v-card-title>
            <v-container>
              <v-row no-gutters >
                <v-col class="pa-2" md="auto">
                    Vendors
                </v-col>
                <v-col class="pa-2">
                  <v-chip
                    small label outlined color="deep-orange"
                    @click="toggleVendorMonitored"
                    v-if="this.only_monitored_vendors">Show all</v-chip>
                  <v-chip
                    small label outlined color="grey"
                    @click="toggleVendorMonitored"
                    v-if="!this.only_monitored_vendors">Show monitored only</v-chip>
                </v-col>
                <v-text-field
                  v-model="search_vendors"
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
            :headers="headers_vendors"
            :items="vendors.results"
            :options.sync="options_vendors"
            :server-items-length="vendors.count"
            :search="search_vendors"
            :footer-props="{
              'items-per-page-options': rowsPerPageItems
            }"
            :loading="loading"
            :items-per-page="rowsPerPage"
            class="elevation-4"
          >

            <!-- Nb vulns -->
            <template v-slot:item.products_count="{ item }">
              <v-chip
                small color="lightgrey">{{item.products_count}}</v-chip>
            </v-chip>
            </template>

            <!-- Monitored -->
            <template v-slot:item.monitored="{ item }">
              <v-chip
                small label outlined color="deep-orange"
                @click="toggleMonitoredVendor(item)"
                v-if="item.monitored">Yes</v-chip>
              <v-chip
                small label outlined color="grey"
                @click="toggleMonitoredVendor(item)"
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
                @click="viewVendor(item.id)"
              >
              </v-icon>
            </template>
          </v-data-table>

          <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
            {{ snackText }}
            <v-btn text @click="snack = false">Close</v-btn>
          </v-snackbar>
        </v-card>
      </v-tab-item>

      <!-- Products -->
      <v-tab-item>
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
                    v-if="this.only_monitored_products">Show all</v-chip>
                  <v-chip
                    small label outlined color="grey"
                    @click="toggleProductMonitored"
                    v-if="!this.only_monitored_products">Show monitored only</v-chip>
                </v-col>
                <v-text-field
                  v-model="search_products"
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
            :headers="headers_products"
            :items="products.results"
            :options.sync="options_products"
            :server-items-length="products.count"
            :search="search_products"
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
                @click="toggleMonitoredProduct(item)"
                v-if="item.monitored">Yes</v-chip>
              <v-chip
                small label outlined color="grey"
                @click="toggleMonitoredProduct(item)"
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
                @click="viewProduct(item.id)"
              >
              </v-icon>
            </template>
          </v-data-table>

          <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
            {{ snackText }}
            <v-btn text @click="snack = false">Close</v-btn>
          </v-snackbar>
        </v-card>
      </v-tab-item>
    </v-tabs>
  </div>
</template>

<script>
import swal from 'sweetalert2';
import _ from 'lodash';

export default {
  name: "VendorsProducts",
  data: () => ({
    vendors: [],
    products: [],
    loading: true,
    limit: 20,
    // totalvendors: 0,
    // totalproducts: 0,
    only_monitored_vendors: false,
    only_monitored_products: false,
    search_vendors: '',
    search_products: '',
    options_vendors: {},
    options_products: {},
    // selected: [],
    headers_vendors: [
      { text: 'Vendor', value: 'name' },
      { text: '# Products', value: 'products_count', align: 'center', sortable: false },
      { text: 'Monitored', value: 'monitored', align: 'center', sortable: false },
      { text: 'Last update', value: 'updated_at' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    headers_products: [
      { text: 'Vendor', value: 'vendor' },
      { text: 'Product', value: 'name' },
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
    search_vendors: _.debounce(function (filter) {
      this.search_vendors = filter;
      this.options_vendors.page = 1;  // reset page count
      this.getDataVendors();
    }, 500),
    search_products: _.debounce(function (filter) {
      this.search_products = filter;
      this.options_products.page = 1;  // reset page count
      this.getDataProducts();
    }, 500),
    only_monitored_vendors: {
      handler() {
        this.getDataVendors();
      },
      deep: true
    },
    only_monitored_products: {
      handler() {
        this.getDataProducts();
      },
      deep: true
    },
    options_vendors: {
      handler() {
        this.getDataVendors();
      },
      deep: true
    },
    options_products: {
      handler() {
        this.getDataProducts();
      },
      deep: true
    }
  },

  methods: {
    getDataVendors() {
      this.loading = true;
      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options_vendors;
        // let search = this.search.trim().toLowerCase();
        this.limit = itemsPerPage;

        let items = this.getVendors(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            items
          });
        }, 300);
      });
      this.loading = false;
    },
    getDataProducts() {
      this.loading = true;
      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options_products;
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
    getVendors(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }
      let monitored = this.only_monitored_vendors ? "&monitored=true" : "";

      this.$api.get('/api/kb/vendors/?limit='+itemsPerPage+'&page='+page+'&search='+this.search_vendors+sorted_by+monitored).then(res => {
        this.loading = false;
        this.vendors = res.data;
        return this.products;
      }).catch(e => {
        this.vendors = [];
        swal.fire({
          title: 'Error',
          text: 'unable to get vendors',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
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
      let monitored = this.only_monitored_products ? "&monitored=true" : "";

      this.$api.get('/api/kb/products/?limit='+itemsPerPage+'&page='+page+'&search='+this.search_products+sorted_by+monitored).then(res => {
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
    toggleMonitoredVendor(item) {
      // save in backend
      let data = {
        'vendor_name': item.name,
        'monitored': !item.monitored,
        'organization_id': localStorage.getItem('org_id')
      };
      this.snack = true;
      this.snackColor = 'secondary';
      this.snackText = 'Monitoring status update in progress...';
      this.$api.post('/api/monitor/vendor/toggle', data).then(res => {
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
    toggleMonitoredProduct(item) {
      // save in backend
      let data = {
        'vendor_name': item.vendor,
        'product_name': item.name,
        'monitored': !item.monitored,
        'organization_id': localStorage.getItem('org_id')
      };
      this.snack = true;
      this.snackColor = 'secondary';
      this.snackText = 'Monitoring status update in progress...';
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
    toggleVendorMonitored() {
      this.only_monitored_vendors = !this.only_monitored_vendors;
      this.options_vendors.page = 1;
    },
    toggleProductMonitored() {
      this.only_monitored_products = !this.only_monitored_products;
      this.options_products.page = 1;
    },
    viewVendor(vendor_id) {
      this.$router.push({ 'path': '/vendor/'+vendor_id });
    },
    viewProduct(product_id) {
      this.$router.push({ 'path': '/product/'+product_id });
    },
  }
};
</script>
