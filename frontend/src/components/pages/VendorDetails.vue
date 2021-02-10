<template>
    <!-- Vendor Details Page -->
    <v-tabs
      left
      background-color="white"
      color="deep-orange accent-4"
    >
      <v-tab>Details</v-tab>
      <v-tab>Products</v-tab>
      <!-- <v-tab>Timeline</v-tab> -->

      <!-- Details -->
      <v-tab-item>
        <v-container fluid grid-list-md>
          <v-layout row wrap>
            <v-flex md3 d-flex align-stretch>
              <v-card color="grey lighten-5" class="flex-grow-1">
                <v-card-title>
                  <v-col class="pa-2" md="auto">
                    Overview
                  </v-col>
                  <v-col class="pa-2">
                    <v-chip
                      small label outlined color="deep-orange"
                      @click="toggleMonitored"
                      v-if="vendor.monitored">Monitored</v-chip>
                    <v-chip
                      small label outlined color="grey"
                      @click="toggleMonitored"
                      v-if="!vendor.monitored">Not monitored</v-chip>
                  </v-col>
                </v-card-title>
                <v-card-text>
                  <span class="font-weight-bold">Name:</span> {{vendor.name}}<br/>
                </v-card-text>
              </v-card>
            </v-flex>
            <v-flex md3 d-flex align-stretch>
              <v-card color="grey lighten-5" class="flex-grow-1">
                <v-col class="pa-2" md="auto">
                  <v-card-title>Statistics</v-card-title>
                </v-col>
                <v-card-text>
                  <span class="font-weight-bold">Vulnerabilities: </span>
                  <v-chip color="deep-orange white--text" :content="this.vulns.count" small>{{vulns.count}}</v-chip>
                  <br/>
                  <span class="font-weight-bold">Products: </span>
                  <v-chip color="deep-orange white--text" small>{{vendor.products_count}}</v-chip>
                </v-card-text>
              </v-card>
            </v-flex>
            <!-- <v-flex md6 d-flex align-stretch>
              <v-card color="grey lighten-5" class="flex-grow-1">
                <v-card-title>Known versions</v-card-title>
                <v-card-text>
                  <v-chip-group
                    v-model="select_pv"
                    active-class="deep-orange--text "
                    multiple
                  >
                    <v-chip
                      color="grey" small label outlined
                      v-for="v in cpes"
                      >{{v.version}}
                    </v-chip>
                  </v-chip-group>
                </v-card-text>
              </v-card>
            </v-flex> -->
          </v-layout>

          <v-layout row wrap>
            <v-flex md12>
              <v-data-table
                :headers="vulns_headers"
                :items="vulns.results"
                :options.sync="options_vulns"
                :server-items-length="vulns.count"
                :items-per-page="limit_vulns"
                :footer-props="{
                  'items-per-page-options': rowsPerPageItems
                }"
                :loading_vulns="loading_vulns"
                class="elevation-4"
                item-key="id"
                multi-sort
              >

                <!-- Rating -->
                <template v-slot:item.score="{ item }">
                  <v-chip
                    :color="getRatingColor(item.score)"
                    class="text-center font-weight-bold"
                    label

                  >{{item.score}}/100</v-chip><br/>
                  <span class="text-caption">CVSSv2: {{item.cvss}}</span><br/>
                  <span class="text-caption">CVSSv3: {{item.cvss3}}</span>
                </template>

                <!-- Summary -->
                <template v-slot:item.summary="{ item }">
                  <div class="py-2">
                    <div class="pb-2">
                      <span class="deep-orange--text font-weight-medium">{{item.cveid}}</span> / PH-{{item.id}}
                      <v-btn
                        color="deep-orange"
                        icon small
                        ><v-icon title="View details" @click="viewVuln(item.id)">mdi-arrow-right-bold-circle-outline</v-icon>
                      </v-btn>
                    </div>
                    <div>
                      {{ item.summary }}
                    </div>
                    <v-chip
                      v-for="p in item.products" :key="p.id"
                      class="vendor-chip"
                      label small link
                      @click="$router.push({ 'path': '/product/'+p.id });"
                      >
                      {{ p.vendor }}: <span class="font-weight-bold">{{p.name}}</span>
                    </v-chip>
                  </div>
                </template>

                <!-- Metadata -->
                <template v-slot:item.metadata="{ item }">
                  <!-- Is exploitable -->
                  <v-chip
                    label link small
                    :color="item.exploit_count>0?'deep-orange':'grey'"
                    class="font-weight-bold"
                    title="Is exploitable?"
                  >{{item.exploit_count}}</v-chip>

                  <!-- Remotely exploitable -->
                  <v-btn
                    :color="item.access.vector=='NETWORK'?'deep-orange':'grey'"
                    icon small
                    ><v-icon title="Is exploitable remotely?">mdi-cloud</v-icon>
                  </v-btn>

                  <!-- Auth Needed -->
                  <v-btn
                    :color="item.access.authentication=='NONE'?'deep-orange':'grey'"
                    icon small
                    ><v-icon title="Require authentication?">mdi-shield-account</v-icon>
                  </v-btn>

                  <!-- In the News/Wild -->
                  <v-btn
                    :color="item.is_in_the_news||item.is_in_the_wild?'deep-orange':'grey'"
                    icon small
                    ><v-icon title="Is in the news or exploited in the wild?">mdi-star</v-icon>
                  </v-btn>
                </template>

                <template v-slot:item.updated_at="{ item }">
                  <span>{{moment(item.updated_at).format('YYYY-MM-DD, hh:mm:ss')}}</span>
                </template>
              </v-data-table>
            </v-flex>
          </v-layout>
        </v-container>
        <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
          {{ snackText }}
          <v-btn text @click="snack = false">Close</v-btn>
        </v-snackbar>
      </v-tab-item>

      <!-- Products -->
      <v-tab-item>
        <v-container fluid grid-list-md>
          <v-layout row wrap>
            <v-flex md12>
              <v-data-table
                :headers="products_headers"
                :items="products.results"
                :options.sync="options_products"
                :server-items-length="products.count"
                :items-per-page="limit_products"
                :footer-props="{
                  'items-per-page-options': rowsPerPageItems
                }"
                :loading_vulns="loading_vulns"
                class="elevation-4"
                item-key="id"
                multi-sort
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
                  <span>{{moment(item.updated_at).format('YYYY-MM-DD, hh:mm:ss')}}</span>
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
            </v-flex>
          </v-layout>
        </v-container>
        <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
          {{ snackText }}
          <v-btn text @click="snack = false">Close</v-btn>
        </v-snackbar>
      </v-tab-item>

      <!-- Timeline -->
      <!-- <v-tab-item>
        <v-container fluid grid-list-md>
          <v-layout row wrap>
            Soon available.
          </v-layout>
        </v-container>
      </v-tab-item> -->

    </v-tabs>

</template>

<script>
import swal from 'sweetalert2';
// import _ from 'lodash';
import Colors from "../../common/colors";
import moment from 'moment';

export default {
  name: "vendordetails",
  mixins: [Colors],
  data: () => ({
    loading_vulns: true,
    loading_products: true,
    vendor_id: "",
    vendor: {},
    products: [],
    vulns: {'results': []},
    limit_vulns: 20,
    limit_products: 20,
    options_vulns: {},
    options_products: {},
    vulns_headers: [
      { text: 'Score', value: 'score', align: 'center', width: "10%" },
      { text: 'Summary', value: 'summary' },
      { text: 'Metadata', value: 'metadata', align: 'center', width: "9%", sortable: false },
      { text: 'Last update', value: 'updated_at', align: 'center', width: "10%" },
    ],
    products_headers: [
      { text: 'Product Name', value: 'name' },
      // { text: 'Vulnerabilities', value: 'name' },
      { text: 'Monitored', value: 'monitored' },
      { text: 'Last update', value: 'updated_at', align: 'center' },
      { text: 'Actions', value: 'action', sortable: false, align: 'center' },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  watch: {
    options_vulns: {
      handler() {
        this.getDataVendor(this.vendor_id);
      },
      deep: true
    },
    options_products: {
      handler() {
        this.getDataProducts(this.vendor_id);
      },
      deep: true
    },
  },
  beforeRouteUpdate(to) {
    this.vendor_id = to.params.vendor_id
  },
  mounted() {
    this.vendor_id = this.$router.currentRoute.params.vendor_id;
    this.options_products.page = 1;  // reset page count
    this.options_vulns.page = 1;  // reset page count
    // this.getDataVendor(this.vendor_id);
    // this.getDataProducts(this.vendor_id);
  },
  methods: {
    getDataVendor(vendor_id) {
      this.loading_vulns = true;
      return new Promise((resolve, reject) => {

        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options_vulns;
        this.limit_vulns = itemsPerPage;

        let vendor = this.getVendor(vendor_id);
        let vulns = this.getVulns(vendor_id, page, this.limit_vulns, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            vendor, vulns
          });
        }, 300);
      });
      this.loading_vulns = false;
    },
    getDataProducts(vendor_id) {
      this.loading_vulns = true;
      return new Promise((resolve, reject) => {

        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options_products;
        this.limit_products = itemsPerPage;

        let products = this.getProducts(vendor_id, page, this.limit_vulns, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            products
          });
        }, 300);
      });
      this.loading_vulns = false;
    },
    getVendor(vendor_id) {
      this.loading_vulns = true;
      this.$api.get('/api/kb/vendors/'+vendor_id).then(res => {
        this.vendor = res.data;
        return this.vendor;
      }).catch(e => {
        this.vendor = {};
        this.loading_vulns = false;
        swal.fire({
          title: 'Error',
          text: 'Unable to get vendor details',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading_vulns = false;
    },
    getProducts(vendor_id, page, itemsPerPage, sortBy="", sortDesc) {
      this.loading_products = true;
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }

      this.$api.get('/api/kb/products/?vendor_id='+vendor_id+'&limit='+itemsPerPage+'&page='+page+'&'+sorted_by).then(res => {
        this.products = res.data;
        return this.products;
      }).catch(e => {
        this.products = [];
        this.loading_vulns = false;
        swal.fire({
          title: 'Error',
          text: 'Unable to get products',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading_products = false;
    },
    viewVuln(vuln_id) {
      this.$router.push({ 'path': '/vulns/'+vuln_id });
    },
    viewProduct(product_id) {
      this.$router.push({ 'path': '/product/'+product_id });
    },
    getVulns(vendor_id, page, itemsPerPage, sortBy="", sortDesc) {
      this.loading_vulns = true;
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }
      this.$api.get('/api/vulns/?vendor='+vendor_id+'&limit='+itemsPerPage+'&page='+page+'&'+sorted_by).then(res => {
        this.vulns = res.data;
        return this.vulns;
      }).catch(e => {
        vulns = {'results': []};
        this.loading_vulns = false;
        swal.fire({
          title: 'Error',
          text: 'Unable to get vulns',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading_vulns = false;
    },
    toggleMonitored() {
      // save in backend
      let data = {
        'vendor_name': this.vendor.name,
        'monitored': !this.vendor.monitored,
        'organization_id': localStorage.getItem('org_id')
      };
      this.$api.post('/api/monitor/vendor/toggle', data).then(res => {
        this.loading_vulns = false;
        if (res){
          this.vendor.monitored = !this.vendor.monitored;
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
        this.loading_vulns = false;
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
        'vendor_name': this.vendor.name,
        'product_name': item.name,
        'monitored': !item.monitored,
        'organization_id': localStorage.getItem('org_id')
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
  }
};
</script>
