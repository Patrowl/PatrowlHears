<template>
    <!-- Package Details Page -->
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
            <!-- Package: {{package}} -->
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
                      v-if="package.monitored">Monitored</v-chip>
                    <v-chip
                      small label outlined color="grey"
                      @click="toggleMonitored"
                      v-if="!package.monitored">Not monitored</v-chip>
                  </v-col>
                </v-card-title>
                <v-card-text>
                  <span class="font-weight-bold">Type:</span> {{package.type}}<br/>
                  <span class="font-weight-bold">Name:</span> {{package.name}}<br/>
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
import Colors from "../../common/colors";
import moment from 'moment';

export default {
  name: "PackageDetails",
  mixins: [Colors],
  data: () => ({
    loading: true,
    package_id: "",
    package: {},
    select_p: [],
    vulns: {'results': []},
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
        this.getDataFromApi(this.package_id);
      },
      deep: true
    },
    filter_version: {
      handler() {
        this.getDataFromApi(this.package_id);
      },
      deep: true
    },
  },
  beforeRouteUpdate(to, from) {
    this.package_id = to.params.package_id;
  },
  mounted() {
    this.package_id = this.$router.currentRoute.params.package_id;
    this.options.page = 1;  // reset page count
  },
  methods: {
    getDataFromApi(package_id) {
      this.loading = true;
      return new Promise((resolve, reject) => {

        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options;
        this.limit = itemsPerPage;

        let pkg = this.getPackage(package_id);
        let vulns = this.getVulns(package_id, page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            pkg, vulns
          });
        }, 300);
      });
      // this.loading = false;
    },
    getPackage(package_id) {
      // this.loading = true;
      this.$api.get('/api/kb/packages/'+package_id).then(res => {
        this.package = res.data;
        return this.package;
      }).catch(e => {
        this.package = {};
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'Unable to get package details',
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
    getVulns(package_id, page, itemsPerPage, sortBy="", sortDesc) {
      // this.loading = true;
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }
      let vuln_url = '/api/vulns/?package='+package_id+'&limit='+itemsPerPage+'&page='+page+'&'+sorted_by;

      this.$api.get(vuln_url).then(res => {
        this.vulns = res.data;
        this.loading = false;
        return this.vulns;
      }).catch(e => {
        vulns = {'results': []};
        // this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'Unable to get vulns',
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
        'package_id': this.package.id,
        'monitored': !this.package.monitored,
        'organization_id': localStorage.getItem('org_id')
      };
      this.$api.post('/api/monitor/package/toggle', data).then(res => {
        // this.loading = false;
        if (res){
          this.package.monitored = !this.package.monitored;
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
  }
};
</script>
