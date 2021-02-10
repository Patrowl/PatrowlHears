<template>
    <!-- Products Details Page -->
    <v-tabs
      left
      background-color="white"
      color="deep-orange accent-4"
    >
      <v-tab>Details</v-tab>
      <v-tab>Timeline</v-tab>

      <!-- Details -->
      <v-tab-item>
        <v-container fluid grid-list-md>
          <v-layout row wrap>
            <!-- Product: {{product}} -->
            <v-flex md3 d-flex align-stretch>
              <v-card color="grey lighten-5" class="flex-grow-1">
                <v-card-title>
                  <v-col class="pa-2" md="auto">
                    Information
                  </v-col>
                  <v-col class="pa-2">
                    <v-chip
                      small label outlined color="deep-orange"
                      @click="toggleMonitored"
                      v-if="product.monitored">Monitored</v-chip>
                    <v-chip
                      small label outlined color="grey"
                      @click="toggleMonitored"
                      v-if="!product.monitored">Not monitored</v-chip>
                  </v-col>
                </v-card-title>
                <v-card-text>
                  <span class="font-weight-bold">Name:</span> {{product.name}}<br/>
                  <span class="font-weight-bold">Vendor:</span> <a @click="viewVendor(product.vendor_id)">{{product.vendor}}</a>
                </v-card-text>
              </v-card>
            </v-flex>
            <v-flex md3 d-flex align-stretch>
              <v-card color="grey lighten-5" class="flex-grow-1">
                <v-card-title>Statistics</v-card-title>
                <v-card-text>
                  <span class="font-weight-bold">Vulnerabilities: </span>
                  <v-chip color="deep-orange white--text" :content="this.vulns.count" small>{{vulns.count}}</v-chip>
                  <br/>
                  <span class="font-weight-bold">Versions: </span>
                  <v-chip color="deep-orange white--text" small>{{cpes.length}}</v-chip>
                </v-card-text>
              </v-card>
            </v-flex>
            <v-flex md6 d-flex align-stretch>
              <v-card color="grey lighten-5" class="flex-grow-1">
                <v-card-title>
                  Known versions
                  <v-icon
                    small link
                    title="Reset selection"
                    @click="filter_version=null;select_pv=[]"
                    class="ml-2"
                  >
                    mdi-reload
                  </v-icon>
                </v-card-title>
                <v-card-text>


                  <v-chip-group
                    v-model="select_pv"
                    active-class="deep-orange--text text--accent-4"
                  >

                    <v-chip
                      small label outlined
                      v-for="v in cpes" :key="v.id"
                      @click="filter_version=v.version"
                      >{{v.version}}
                    </v-chip>
                  </v-chip-group>
                </v-card-text>
              </v-card>
            </v-flex>
          </v-layout>

          <v-layout row wrap>
            <v-flex md12>
              <v-data-table
                :headers="vulns_headers"
                :items="vulns.results"
                :options.sync="options"
                :server-items-length="vulns.count"
                :search="search"
                :items-per-page="20"
                :footer-props="{
                  'items-per-page-options': rowsPerPageItems
                }"
                :loading="loading"
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
                      @click="viewProduct(p.id)"
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
      </v-tab-item>

      <!-- Timeline -->
      <v-tab-item>
        <v-container fluid grid-list-md>
          <v-layout row wrap>
            Soon available.
          </v-layout>
        </v-container>
      </v-tab-item>

    </v-tabs>

</template>

<script>
import swal from 'sweetalert2';
import _ from 'lodash';
import VClamp from 'vue-clamp';
import Colors from "../../common/colors";
import moment from 'moment';

export default {
  name: "productdetails",
  mixins: [Colors],
  components: {
    VClamp
  },
  data: () => ({
    loading: true,
    product_id: "",
    product: {},
    select_pv: [],
    vulns: {'results': []},
    cpes: [],
    limit: 20,
    search: '',
    filter_version: null,
    options: {},
    selected: [],
    vulns_headers: [
      { text: 'Score', value: 'score', align: 'center', width: "10%" },
      { text: 'Summary', value: 'summary' },
      { text: 'Metadata', value: 'metadata', align: 'center', width: "9%", sortable: false },
      { text: 'Last update', value: 'updated_at', align: 'center', width: "10%" },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  watch: {
    options: {
      handler() {
        this.getDataFromApi(this.product_id);
      },
      deep: true
    },
    filter_version: {
      handler() {
        this.getDataFromApi(this.product_id);
      },
      deep: true
    },
  },
  beforeRouteUpdate(to, from) {
    this.product_id = to.params.product_id;
  },
  mounted() {
    this.product_id = this.$router.currentRoute.params.product_id;
    this.options.page = 1;  // reset page count
  },
  methods: {
    getDataFromApi(product_id) {
      this.loading = true;
      return new Promise((resolve, reject) => {

        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options;
        this.limit = itemsPerPage;

        let product = this.getProduct(product_id);
        let vulns = this.getVulns(product_id, page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            product, vulns
          });
        }, 300);
      });
      // this.loading = false;
    },
    getProduct(product_id) {
      // this.loading = true;
      this.$api.get('/api/kb/detailed-products/'+product_id).then(res => {
        this.product = res.data;
        this.cpes = this.product.versions;
        return this.product;
      }).catch(e => {
        this.product = {};
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get product details',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      // this.loading = false;
    },
    viewVuln(vuln_id) {
      this.$router.push({ 'name': 'VulnDetails', 'params': { 'vuln_id': vuln_id } });
    },
    viewProduct(product_id) {
      const path = '/product/'+product_id;
      if (this.$route.path != path) {
        // Bug here
        this.product_id = product_id
        this.$router.push({ 'path': path });
      }
    },
    getVulns(product_id, page, itemsPerPage, sortBy="", sortDesc) {
      // this.loading = true;
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }
      let vuln_url = '/api/vulns/?product='+product_id+'&limit='+itemsPerPage+'&page='+page+'&'+sorted_by;
      if (this.filter_version != null && this.filter_version != ''){
        vuln_url += '&product_version='+this.filter_version+'&vendor_name='+this.product.vendor+'&product_name='+this.product.name
      }
      this.$api.get(vuln_url).then(res => {
        this.vulns = res.data;
        this.loading = false;
        return this.vulns;
      }).catch(e => {
        vulns = {'results': []};
        // this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get vulns',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading = false;
    },
    toggleMonitored() {
      // save in backend
      let data = {
        'vendor_name': this.product.vendor,
        'product_name': this.product.name,
        'monitored': !this.product.monitored,
        'organization_id': localStorage.getItem('org_id')
      };
      this.$api.post('/api/monitor/product/toggle', data).then(res => {
        // this.loading = false;
        if (res){
          this.product.monitored = !this.product.monitored;
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
        // this.loading = false;
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
    viewVendor(vendor_id) {
      this.$router.push({ 'path': '/vendor/'+vendor_id });
    },
  }
};
</script>
