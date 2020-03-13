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
                    Product
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
                  <span class="font-weight-bold">Vendor:</span> {{product.vendor}}
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
                <v-card-title>Known versions</v-card-title>
                <v-card-text>
                  <v-chip-group
                    v-model="select_pv"
                    active-class="deep-orange--text grey"
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
                show-select
                multi-sort
              >

              <template v-slot:item.summary="{ item }">
                <v-clamp autoresize :max-lines="1">
                  {{ item.summary }}
                  <button
                    v-if="expanded || clamped"
                    slot="after"
                    slot-scope="{ toggle, expanded, clamped }"
                    class="toggle btn btn-sm"
                    @click="toggle"
                  >
                    {{ ' more' }}
                  </button>
                </v-clamp>
              </template>

              <!-- Rating -->
              <template v-slot:item.score="{ item }">
                <v-chip
                  :color="getRatingColor(item.score)"
                  class="text-center"
                  small
                >
                {{item.score}}
                </v-chip>
              </template>

              <!-- Is exploitable -->
              <template v-slot:item.is_exploitable="{ item }">
                <v-chip
                  :color="getBool(item.is_exploitable)"
                  class="text-center"
                  small
                  label
                >
                </v-chip>
              </template>

              <!-- Is confirmed -->
              <template v-slot:item.is_confirmed="{ item }">
                <v-icon
                  small
                  class="mdi mdi-check"
                  color="gray"
                  v-if="item.is_confirmed == true"
                >
                </v-icon>
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
                  @click="viewVuln(item.id)"
                >
                </v-icon>
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
            Timeline (Todo)
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
    select_pv: "",
    vulns: {'results': []},
    cpes: [],
    limit: 20,
    search: '',
    options: {},
    selected: [],
    vulns_headers: [
      { text: 'PHID', value: 'id' },
      { text: 'CVE', value: 'cveid', width: '150px' },
      { text: 'Summary', value: 'summary' },
      { text: 'CVSSv2', value: 'cvss', align: 'center' },
      { text: 'Score', value: 'score', align: 'center' },
      { text: 'Exploits', value: 'exploit_count', align: 'center' },
      { text: 'Confirm ?', value: 'is_confirmed', align: 'center' },
      { text: 'Last update', value: 'updated_at', align: 'center' },
      { text: 'Actions', value: 'action', sortable: false, align: 'center' },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  beforeRouteUpdate(to) {
    this.product_id = to.params.product_id
  },
  mounted() {
    this.product_id = this.$router.currentRoute.params.product_id;
    this.getDataFromApi(this.product_id);
  },
  methods: {
    getDataFromApi(product_id) {
      this.loading = true;
      return new Promise((resolve, reject) => {

        let product = this.getProduct(product_id);
        let vulns = this.getVulns(product_id);

        setTimeout(() => {
          resolve({
            product, vulns
          });
        }, 300);
      });
      this.loading = false;
    },
    getProduct(product_id) {
      this.loading = true;
      this.$api.get('/api/kb/detailed-products/'+product_id).then(res => {
      // this.$api.get('/api/kb/products/'+product_id).then(res => {
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
      this.loading = false;
    },
    viewVuln(vuln_id) {
      this.$router.push({ 'name': 'VulnDetails', 'params': { 'vuln_id': vuln_id } });
    },
    getVulns(product_id) {
      this.loading = true;
      this.$api.get('/api/vulns/?product='+product_id).then(res => {
        this.vulns = res.data;
        return this.vulns;
      }).catch(e => {
        vulns = {'results': []};
        this.loading = false;
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
        'monitored': !this.product.monitored
      };
      this.$api.post('/api/monitor/product/toggle', data).then(res => {
        this.loading = false;
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
