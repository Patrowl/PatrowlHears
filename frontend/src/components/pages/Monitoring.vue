<template>
  <div>

    <!-- Monitored assets
    <v-divider></v-divider> -->
    <v-tabs
      left
      background-color="white"
      color="deep-orange accent-4"
    >

      <v-tab>Vendors</v-tab>
      <v-tab>Products</v-tab>
      <v-tab>Packages</v-tab>
      <v-tab>Vulns</v-tab>

      <!-- Vendors -->
      <v-tab-item>
        <v-card>
          <v-card-title>
            <v-container>
              <v-row no-gutters >
                <v-col class="pa-2 mr-4" md="auto">
                    Monitored Vendors
                    <v-menu
                      bottom
                      right
                      :offset-x="true"
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          icon
                          outlined
                          x-small
                          color="deep-orange"
                          v-bind="attrs"
                          v-on="on"
                        >
                          <v-icon>mdi-dots-horizontal</v-icon>
                        </v-btn>
                      </template>

                      <v-list>
                        <v-list-item @click="goToPage('/vendors')">
                          <v-list-item-title>Add new vendors</v-list-item-title>
                        </v-list-item>
                        <v-list-item>
                          <v-list-item-title>
                            <input type="button" id="import_monitored" value="Import monitored" onclick="document.getElementById('file').click();" />
                            <input
                             ref="upload"
                             id="file"
                             type="file"
                             name="file-upload"
                             style="display:none;"
                             accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                             @change="onImportFileChange"/>
                          </v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="exportMonitored('vendors')">
                          <v-list-item-title>Export monitored Vendors</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="exportMonitored('all')">
                          <v-list-item-title>Export all monitored</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                </v-col>
                  <v-text-field
                    v-model="search_vendors"
                    append-icon="mdi-magnify"
                    label="Search"
                    single-line
                    hide-details
                    md="6"
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
            item-key="name"
            show-select
          >

            <!-- Nb products -->
            <template v-slot:item.products_count="{ item }">
              <v-chip
                small color="lightgrey">{{item.products_count}}</v-chip>
            </v-chip>
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
          <v-btn
            absolute
            dark
            fab
            bottom
            left
            color="deep-orange"
            @click="goToPage('/vendors')">
            <v-icon>mdi-plus</v-icon>
          </v-btn>

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
                <v-col class="pa-2 mr-4" md="auto">
                    Monitored Products
                    <v-menu
                      bottom
                      right
                      :offset-x="true"
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          icon
                          outlined
                          x-small
                          color="deep-orange"
                          v-bind="attrs"
                          v-on="on"
                        >
                          <v-icon>mdi-dots-horizontal</v-icon>
                        </v-btn>
                      </template>

                      <v-list>
                        <v-list-item @click="goToPage('/vendors')">
                          <v-list-item-title>Add new product(s)</v-list-item-title>
                        </v-list-item>
                        <v-list-item>
                          <v-list-item-title>
                            <input type="button" id="import_monitored" value="Import monitored" onclick="document.getElementById('file').click();" />
                            <input
                             ref="upload"
                             id="file"
                             type="file"
                             name="file-upload"
                             style="display:none;"
                             accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                             @change="onImportFileChange"/>
                          </v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="exportMonitored('products')">
                          <v-list-item-title>Export monitored Products</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="exportMonitored('all')">
                          <v-list-item-title>Export all monitored</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
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
            item-key="id"
            show-select
          >

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
          <v-btn
            absolute
            dark
            fab
            bottom
            left
            color="deep-orange"
            @click="goToPage('/vendors')">
            <v-icon>mdi-plus</v-icon>
          </v-btn>

          <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
            {{ snackText }}
            <v-btn text @click="snack = false">Close</v-btn>
          </v-snackbar>
        </v-card>
      </v-tab-item>

      <!-- Packages -->
      <v-tab-item>
        <v-card>
          <v-card-title>
            <v-container>
              <v-row no-gutters >
                <v-col class="pa-2 mr-4" md="auto">
                    Monitored Packages
                    <v-menu
                      bottom
                      right
                      :offset-x="true"
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          icon
                          outlined
                          x-small
                          color="deep-orange"
                          v-bind="attrs"
                          v-on="on"
                        >
                          <v-icon>mdi-dots-horizontal</v-icon>
                        </v-btn>
                      </template>

                      <v-list>
                        <v-list-item @click="goToPage('/packages')">
                          <v-list-item-title>Add new package(s)</v-list-item-title>
                        </v-list-item>
                        <v-list-item>
                          <v-list-item-title>
                            <input type="button" id="import_monitored" value="Import monitored" onclick="document.getElementById('file').click();" />
                            <input
                             ref="upload"
                             id="file"
                             type="file"
                             name="file-upload"
                             style="display:none;"
                             accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                             @change="onImportFileChange"/>
                          </v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="exportMonitored('packages')">
                          <v-list-item-title>Export monitored Packages</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="exportMonitored('all')">
                          <v-list-item-title>Export all monitored</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
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
            item-key="id"
            show-select
          >

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
          <v-btn
            absolute
            dark
            fab
            bottom
            left
            color="deep-orange"
            @click="goToPage('/packages')">
            <v-icon>mdi-plus</v-icon>
          </v-btn>

          <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
            {{ snackText }}
            <v-btn text @click="snack = false">Close</v-btn>
          </v-snackbar>
        </v-card>
      </v-tab-item>

      <!-- Vulns -->
      <v-tab-item>
        <v-card>
          <v-card-title>
            <v-container>
              <v-row no-gutters >
                <v-col class="pa-2 mr-4" md="auto">
                    Monitored Vulns
                    <v-menu
                      bottom
                      right
                      :offset-x="true"
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          icon
                          outlined
                          x-small
                          color="deep-orange"
                          v-bind="attrs"
                          v-on="on"
                        >
                          <v-icon>mdi-dots-horizontal</v-icon>
                        </v-btn>
                      </template>

                      <v-list>
                        <v-list-item @click="goToPage('/vulns')">
                          <v-list-item-title>Add new vuln(s)</v-list-item-title>
                        </v-list-item>
                        <v-list-item>
                          <v-list-item-title>
                            <input type="button" id="import_monitored" value="Import monitored" onclick="document.getElementById('file').click();" />
                            <input
                             ref="upload"
                             id="file"
                             type="file"
                             name="file-upload"
                             style="display:none;"
                             accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                             @change="onImportFileChange"/>
                          </v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="exportMonitored('vulns')">
                          <v-list-item-title>Export monitored Vulns</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="exportMonitored('all')">
                          <v-list-item-title>Export all monitored</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                </v-col>
                <v-text-field
                  v-model="search_vulns"
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
            :headers="headers_vulns"
            :items="vulns.results"
            :options.sync="options_vulns"
            :server-items-length="vulns.count"
            :search="search_vulns"
            :footer-props="{
              'items-per-page-options': rowsPerPageItems
            }"
            :loading="loading"
            :items-per-page="rowsPerPage"
            class="elevation-4"
            item-key="item"
            show-select
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

          <!-- Updated at -->
          <template v-slot:item.updated_at="{ item }">
            <span>{{moment(item.updated_at).format('YYYY-MM-DD, hh:mm')}}</span>
          </template>

          </v-data-table>
          <v-btn
            absolute
            dark
            fab
            bottom
            left
            color="deep-orange"
            @click="goToPage('/vulns')">
            <v-icon>mdi-plus</v-icon>
          </v-btn>

          <v-snackbar v-model="snack" :timeout="snackTimeout" :color="snackColor">
            {{ snackText }}
            <v-btn text @click="snack = false">Close</v-btn>
          </v-snackbar>
        </v-card>
      </v-tab-item>
    </v-tabs>
  </div>
</template>

<script>
import Colors from "../../common/colors";
import Download from "../../common/download";
import swal from 'sweetalert2';
import _ from 'lodash';

export default {
  name: "Monitoring",
  mixins: [Colors, Download],
  data: () => ({
    vendors: [],
    products: [],
    packages: [],
    vulns: [],
    loading: true,
    limit: 20,
    search_vendors: '',
    search_products: '',
    search_packages: '',
    search_vulns: '',
    options_vendors: {},
    options_products: {},
    options_packages: {},
    options_vulns: {},
    headers_vendors: [
      { text: 'Vendor', value: 'name' },
      { text: '# Products', value: 'products_count', align: 'center', sortable: false },
      { text: 'Last update', value: 'updated_at' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    headers_products: [
      { text: 'Vendor', value: 'vendor' },
      { text: 'Product', value: 'name' },
      { text: 'Last update', value: 'updated_at' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    headers_packages: [
      { text: 'Type', value: 'type' },
      { text: 'Package', value: 'name' },
      { text: 'Last update', value: 'updated_at' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    headers_vulns: [
      { text: 'Score', value: 'score', align: 'center', width: "10%" },
      { text: 'Summary', value: 'summary' },
      { text: 'Metadata', value: 'metadata', align: 'center', width: "8%", sortable: false },
      { text: 'Last update', value: 'updated_at', align: 'center', width: "12%" },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    rowsPerPage: 10,
    snack: false,
    snackColor: '',
    snackText: '',
    snackTimeout: 3000,
  }),
  mounted() {
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
    search_packages: _.debounce(function (filter) {
      this.search_packages = filter;
      this.options_packages.page = 1;  // reset page count
      this.getDataPackages();
    }, 500),
    search_vulns: _.debounce(function (filter) {
      this.search_vulns = filter;
      this.options_vulns.page = 1;  // reset page count
      this.getDataVulns();
    }, 500),
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
    },
    options_packages: {
      handler() {
        this.getDataPackages();
      },
      deep: true
    },
    options_vulns: {
      handler() {
        this.getDataVulns();
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
    getDataVulns() {
      this.loading = true;
      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options_vulns;
        this.limit = itemsPerPage;

        let items = this.getVulns(page, this.limit, sortBy, sortDesc);

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

      this.$api.get('/api/kb/vendors/?monitored=true&limit='+itemsPerPage+'&page='+page+'&search='+this.search_vendors+sorted_by).then(res => {
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

      this.$api.get('/api/kb/products/?monitored=true&limit='+itemsPerPage+'&page='+page+'&search='+this.search_products+sorted_by).then(res => {
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
    getPackages(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }

      this.$api.get('/api/kb/packages/?monitored=true&limit='+itemsPerPage+'&page='+page+'&name='+this.search_packages+sorted_by).then(res => {
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
    getVulns(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }

      this.$api.get('/api/vulns/?monitored=true&limit='+itemsPerPage+'&page='+page+'&search='+this.search_products+sorted_by).then(res => {
        this.loading = false;
        this.vulns = res.data;
        return this.vulns;
      }).catch(e => {
        this.vulns = [];
        swal.fire({
          title: 'Error',
          text: 'unable to get vulns',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
    },
    viewVendor(vendor_id) {
      this.$router.push({ 'path': '/vendor/'+vendor_id });
    },
    viewProduct(product_id) {
      this.$router.push({ 'path': '/product/'+product_id });
    },
    viewPackage(package_id) {
      this.$router.push({ 'path': '/packages/'+package_id });
    },
    viewVuln(vuln_id) {
      this.$router.push({ 'path': '/vulns/'+vuln_id });
    },
    goToPage(page) {
      this.$router.push({ 'path': page });
    },
    exportMonitored(type) {
      this.snack = true;
      this.snackColor = 'warning';
      this.snackText = 'Preparing export...';
      this.$api.get('/api/monitor/export/'+type).then(res => {
        this.forceFileDownload(res, 'ph_export_monitored_'+type+'.csv');
        this.snack = true;
        this.snackColor = 'success';
        this.snackText = 'Monitored assets successfuly exported';
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to export monitored assets';
      });
    },
    onImportFileChange(e) {
      var files = e.target.files || e.dataTransfer.files;
      if (!files.length)
        return;
      const formData = new FormData;
      formData.append('file', files[0]);
      this.snack = true;
      this.snackColor = 'warning';
      this.snackText = 'Importing...';

      this.$api.post('/api/monitor/import', formData).then(res => {
        this.snack = true;
        this.snackColor = 'success';
        this.snackText = 'Monitored assets successfuly uploaded';
        this.options_vendors.page = 1;
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to import monitored assets';
      });
    },
  }
};
</script>
