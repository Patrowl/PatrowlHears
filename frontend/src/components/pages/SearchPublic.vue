<template>
  <v-container>
    <v-row>
      <v-col class="pa-2" cols="10">
        <v-text-field
          class="pt-0"
          v-model="appsearch"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
      </v-col>
      <v-col class="pa-2" md="2">
        <v-slider
          v-model="search_slider_min"
          label="Min Score"
          min="0"
          max="100"
          color="deep-orange"
          track-color="grey"
          thumb-label
          hide-details
        ></v-slider>
        <v-slider
          v-model="search_slider_max"
          label="Max Score"
          min="0"
          max="100"
          color="grey"
          thumb-color="deep-orange"
          track-color="deep-orange"
          thumb-label
          hide-details
        ></v-slider>
      </v-col>
    </v-row>

    <v-row v-if="showAdvancedFilters">
      <v-col cols="12">
        <v-divider></v-divider>
        <advanced-search scope='vulns' v-on:advanced_search_filters="updateAdvancedSearchFilters"></advanced-search>
      </v-col>
    </v-row>

    <v-btn
      depressed tile block
      v-if="!showAdvancedFilters"
      @click="showAdvancedFilters=true"
      label="coic"
    ><v-icon>mdi-chevron-down</v-icon>Show advanced filters<v-icon>mdi-chevron-down</v-icon></v-btn>
    <v-btn
      depressed tile block
      v-else
      @click="showAdvancedFilters=!showAdvancedFilters"
      label="coic"
    ><v-icon>mdi-chevron-up</v-icon>Hide advanced filters<v-icon>mdi-chevron-up</v-icon></v-btn>

    <v-tabs
      left
      background-color="white"
      color="deep-orange accent-4"
      class="mt-1"
    >
      <v-tab>
        <v-badge color="deep-orange" v-if="this.vulns.count > 0" :content="this.vulns.count">Vulnerabilities</v-badge>
        <v-badge color="grey" v-if="this.vulns.count == null || this.vulns.count == 0" content="0">Vulnerabilities</v-badge>
      </v-tab>
      <v-tab>
        <v-badge color="deep-orange"  v-if="this.exploits.count > 0" :content="this.exploits.count">Exploits</v-badge>
        <v-badge color="grey" v-if="this.exploits.count == null || this.exploits.count == 0" content="0">Exploits</v-badge>
      </v-tab>
      <v-tab>
        <v-badge color="deep-orange"  v-if="this.threats.count > 0" :content="this.threats.count">Threat activities</v-badge>
        <v-badge color="grey" v-if="this.threats.count == null || this.threats.count == 0" content="0">Threat activities</v-badge>
      </v-tab>
      <v-tab>
        <v-badge color="deep-orange"  v-if="this.advisories.count > 0" :content="this.advisories.count">Advisories</v-badge>
        <v-badge color="grey" v-if="this.advisories.count == null || this.advisories.count == 0" content="0">Advisories</v-badge>
      </v-tab>
      <v-tab>
        <v-badge color="deep-orange"  v-if="this.tools.count > 0" :content="this.tools.count">Tools</v-badge>
        <v-badge color="grey" v-if="this.tools.count == null || this.tools.count == 0" content="0">Tools</v-badge>
      </v-tab>

      <!-- Vulns -->
      <v-tab-item>
        <v-data-table
          :headers="headers_vulns"
          :items="vulns.results"
          :options.sync="options_vulns"
          :server-items-length="vulns.count"
          :items-per-page="limit_vulns"
          :footer-props="{
            'items-per-page-options': rowsPerPageItems
          }"
          :loading="loading_vulns"
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
            <span class="text-caption">CVSSv2: {{item.cvss}}</span>
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
                <v-icon
                  color="deep-orange"
                  title="Download as JSON file"
                  @click="downloadVuln(item.id, 'json')">mdi-download</v-icon>
                <v-icon
                  color="deep-orange"
                  title="Send vulnerabilty as email"
                  @click="selected_vuln_id=item.id ; dialog_sendmail=true">mdi-email-send-outline</v-icon>
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
      </v-tab-item>

      <!-- Exploits -->
      <v-tab-item>
        <v-data-table
          :headers="headers_exploits"
          :items="exploits.results"
          :options.sync="options_exploits"
          :server-items-length="exploits.count"
          :footer-props="{
            'items-per-page-options': rowsPerPageItems
          }"
          :loading="loading_exploits"
          class="elevation-4"
          item-key="id"
        >
          <!-- Relevancy level -->
          <template v-slot:item.relevancy_level="{ item }">
            <!-- 1 -->
            <v-icon x-small class="mdi mdi-clock-time-six" color="yellow" v-for="n in 1" :key='n' v-if="item.relevancy_level == 1"></v-icon>
            <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 4" :key='n' v-if="item.relevancy_level == 1"></v-icon>
            <!-- 2 -->
            <v-icon x-small class="mdi mdi-clock-time-six" color="orange" v-for="n in 2" :key='n' v-if="item.relevancy_level == 2"></v-icon>
            <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 3" :key='n' v-if="item.relevancy_level == 2"></v-icon>
            <!-- 3 -->
            <v-icon x-small class="mdi mdi-clock-time-six" color="orange darken-4" v-for="n in 3" :key='n' v-if="item.relevancy_level == 3"></v-icon>
            <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 2" :key='n' v-if="item.relevancy_level == 3"></v-icon>
            <!-- 4 -->
            <v-icon x-small class="mdi mdi-clock-time-six" color="red" v-for="n in 4" :key='n' v-if="item.relevancy_level == 4"></v-icon>
            <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 1" :key='n' v-if="item.relevancy_level == 4"></v-icon>
            <!-- 5 -->
            <v-icon x-small class="mdi mdi-clock-time-six" color="red darken-4" v-for="n in 5" :key='n' v-if="item.relevancy_level == 5"></v-icon>
          </template>

          <!-- vp at -->
          <template v-slot:item.vp="{ item }">
            <v-chip
              v-for="p in item.products" :key="p.id"
              class="vendor-chip"
              label small link
              @click="$router.push({ 'path': '/product/'+p.id });"
              >
              {{ p.vendor }}: <span class="font-weight-bold">{{p.name}}</span>
            </v-chip>
          </template>

          <!-- Updated at -->
          <template v-slot:item.updated_at="{ item }">
            <span>{{moment(item.updated_at).format('YYYY-MM-DD')}}</span>
          </template>

        </v-data-table>
      </v-tab-item>

      <!-- Threats -->
      <v-tab-item>
      </v-tab-item>

      <!-- Advisories -->
      <v-tab-item>
      </v-tab-item>

      <!-- Tools -->
      <v-tab-item>
      </v-tab-item>
    </v-tabs>

    <DialogSendVulnByEmail :vuln_id="selected_vuln_id" :visible="dialog_sendmail" @close="dialog_sendmail=false"/>

  </v-container>
</template>

<script>
import swal from 'sweetalert2';
import _ from 'lodash';
import router from "../../router";
import Colors from "../../common/colors";
import Download from "../../common/download";
import DialogSendVulnByEmail from '@/components/general/dialogs/SendVulnByEmail'
import AdvancedSearch from '@/components/pages/AdvancedSearch.vue';

export default {
  name: "Search",
  mixins: [Colors, Download],
  components: {
    AdvancedSearch, DialogSendVulnByEmail
  },
  data: () => ({
    results: [],
    vulns: [],
    exploits: [],
    threats: [],
    advisories: [],
    tools: [],
    loading_vulns: true,
    limit_vulns: 10,
    options_vulns: { sortBy: [] },
    headers_vulns: [
      { text: 'Score', value: 'score', align: 'center', width: "10%" },
      { text: 'Summary', value: 'summary' },
      { text: 'Metadata', value: 'metadata', align: 'center', width: "8%", sortable: false },
      { text: 'Last update', value: 'updated_at', align: 'center', width: "12%" },
    ],
    loading_exploits: true,
    limit_exploits: 10,
    options_exploits: { sortBy: [] },
    headers_exploits: [
      { text: 'Relevancy', value: 'relevancy_level' },
      { text: 'Link', value: 'link', width: "50%" },
      { text: 'Products', value: 'vp', sortable: false },
      { text: 'Last update', value: 'updated_at' },
      // { text: 'Actions', value: 'action', sortable: false },
    ],
    loading_threats: true,
    limit_threats: 10,
    options_threats: { sortBy: [] },
    headers_threats: [
      { text: 'Link', value: 'link', width: "50%" },
      { text: 'Products', value: 'vp', sortable: false },
      { text: 'Last update', value: 'updated_at' },
      // { text: 'Actions', value: 'action', sortable: false },
    ],
    rowsPerPageItems: [10, 25, 50, 100],
    appsearch: '',
    showAdvancedFilters: false,
    extra_filters: '',
    search_slider_min: 0,
    search_slider_max: 100,
    dialog_sendmail: false,
    selected_vuln_id: null,
    notification_data: {
      'emails': ''
    },
    // snackbar
    snack: false,
    snackColor: '',
    snackText: '',
    // appsearch: this.$route.params.appsearch
  }),
  beforeRouteUpdate(to) {
    this.appsearch = to.params.appsearch
  },
  mounted() {
    this.appsearch = this.$router.currentRoute.params.appsearch;
  },
  watch: {
    // appsearch: {
    //   handler(filter) {
    //     console.log("coucou")
    //     console.log(filter)
    //     this.appsearch = filter;
    //
    //     if (this.appsearch != null) {
    //       this.options_vulns.page = 1;  // reset page count
    //       // this.options_exploits.page = 1;  // reset page count
    //       // this.options_threats.page = 1;  // reset page count
    //       // this.getDataFromApi();
    //     } else {
    //       this.loading_vulns = false;
    //       // this.loading_exploits = false;
    //       // this.loading_threats = false;
    //     }
    //   }
    // },
    appsearch: _.debounce(function (filter) {
      console.log("coucou")
      this.appsearch = filter;
      this.options_vulns.page = 1;  // reset page count
      this.getDataFromApi();
    }, 500),
    options_vulns: {
      handler() {
        if (this.appsearch != null) {
          this.getDataFromApi(this.extra_filters);
        }
      },
      deep: true
    },
  },
  methods: {
    getDataFromApi(extra_filters) {
      this.getDataFromApiVuln(extra_filters);
      // this.getDataFromApiExploits(extra_filters);
      // this.getDataFromApiThreats(extra_filters);
    },
    getDataFromApiVuln(extra_filters) {
      this.loading_vulns = true;
      return new Promise((resolve, reject) => {
        const { sortBy, sortDesc, page, itemsPerPage } = this.options_vulns;
        let vulns = this.getVulns(page, this.limit_vulns, sortBy, sortDesc, extra_filters);

        setTimeout(() => { resolve({ vulns }); }, 300);
      });
      this.loading_vulns = false;
    },
    getDataFromApiExploits(extra_filters) {
      this.loading_exploits = true;
      return new Promise((resolve, reject) => {
        const { sortBy, sortDesc, page, itemsPerPage } = this.options_exploits;
        let exploits = this.getExploits(page, this.limit_exploits, sortBy, sortDesc, extra_filters);

        setTimeout(() => { resolve({ exploits }); }, 300);
      });
      this.loading_exploits = false;
    },
    getDataFromApiThreats(extra_filters) {
      this.loading_threats = true;
      return new Promise((resolve, reject) => {
        const { sortBy, sortDesc, page, itemsPerPage } = this.options_threats;
        let threats = this.getThreats(page, this.limit_threats, sortBy, sortDesc, extra_filters);

        setTimeout(() => { resolve({ threats }); }, 300);
      });
      this.loading_threats = false;
    },
    updateAdvancedSearchFilters(filters){
      this.extra_filters = filters;
      this.getDataFromApi(filters);
    },
    getVulns(page, itemsPerPage, sortBy, sortDesc, extra_filters) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }

      if (extra_filters == null || extra_filters == '') {
        extra_filters = "&score__gte="+this.search_slider_min+"&score__lte="+this.search_slider_max
      }

      this.$api.get('/api/public/vulns/?limit='+itemsPerPage+'&page='+page+'&search='+this.appsearch+sorted_by+extra_filters).then(res => {
        this.vulns = res.data;
        this.loading_vulns = false;
        return this.vulns;
      }).catch(e => {
        this.vulns = [];
        this.loading_vulns = false;
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to get vulns.';
      });
    },
    viewVuln(vuln_id) {
      this.$router.push({ 'name': 'VulnDetailsPublic', 'params': { 'vuln_id': vuln_id } });
    },
    downloadVuln(vuln_id, format='json') {
      this.$api.get('/api/public/vulns/'+vuln_id+'/export/'+format, {responseType: 'arraybuffer'}).then(res => {
        this.forceFileDownload(res, 'vuln_export_'+vuln_id+'.'+format);
        this.snack = true;
        this.snackColor = 'success';
        this.snackText = 'Vulnerability details available.';
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to download vulnerability details.';
      });
      this.loading = false;
    },
    sendEmailVuln(vuln_id) {
      this.$api.post('/api/public/vulns/'+vuln_id+'/export/email', this.notification_data).then(res => {
        this.snack = true;
        this.snackColor = 'success';
        this.snackText = 'Vulnerability details successfuly sent by mail.';
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to send vulnerability details.';
      });
      this.dialog_sendmail = false;
    },
    getExploits(page, itemsPerPage, sortBy, sortDesc, extra_filters) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }
      this.$api.get('/api/public/exploits/?limit='+itemsPerPage+'&page='+page+'&search='+this.appsearch+sorted_by+extra_filters).then(res => {
        this.exploits = res.data;
        this.loading_exploits = false;
        return this.exploits;
      }).catch(e => {
        this.exploits = [];
        this.loading_exploits = false;
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to get exploits.';
      });
    },
    getThreats(page, itemsPerPage, sortBy, sortDesc, extra_filters) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }
      this.$api.get('/api/public/threats/?limit='+itemsPerPage+'&page='+page+'&search='+this.appsearch+sorted_by+extra_filters).then(res => {
        this.threats = res.data;
        this.loading_threats = false;
        return this.threats;
      }).catch(e => {
        this.threats = [];
        this.loading_threats = false;
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to get threat news.';
      });
    },
    getBoolValue(b) {
      return b?'Yes':'No';
    },
  }
};
</script>

<style>
dl {
  margin: unset;
}

dt, dd {
  margin-inline-start: 5px;
}

dt {
  clear: both;
  float: left;
  clear: left;
  width: 100px;
  text-align: left;
  font-weight: bold;
  font-size: 0.875rem;
}
/* dt::after {
  content: ":";
} */
</style>
