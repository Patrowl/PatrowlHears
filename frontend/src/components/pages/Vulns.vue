<template>
  <div>
    <v-card>
      <v-card-title class="py-0">
        <!-- Vulnerabilities -->
        <v-container>
          <v-row>
            <v-col class="pa-2" md="auto" >
                Vulnerabilities<br/>
            <!-- </v-col>
            <v-col class="pa-2"> -->
              <v-chip
                small label outlined :color="getBoolColor(this.show_all)"
                @click="toggleShowAll()">All</v-chip>&nbsp;
              <v-chip
                small label outlined :color="getBoolColor(this.show_last_day)"
                @click="toggleShowLastDay()">Last 24h</v-chip>&nbsp;
              <v-chip
                small label outlined :color="getBoolColor(this.show_last_week)"
                @click="toggleShowLastWeek()">Last Week</v-chip>
            </v-col>
            <v-col class="pa-2" md="6">
              <v-text-field
                class="pt-0"
                v-model="search"
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
        </v-container>
      </v-card-title>

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

      <v-data-table
        :headers="headers"
        :items="vulns.results"
        :options.sync="options"
        :server-items-length="vulns.count"
        :search="search"
        :items-per-page="limit"
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
              v-for="p in item.products.slice(0, 5)" :key="p.id"
              class="vendor-chip"
              label small link
              @click="$router.push({ 'path': '/product/'+p.id });"
              >
              {{ p.vendor }}: <span class="font-weight-bold">{{p.name}}</span>
            </v-chip>
            <span v-if="item.products.length > 5" @click="viewVuln(item.id)">
              +
            </span>
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

        <!-- Monitored -->
        <template v-slot:item.monitored="{ item }">
          <v-chip
            small label outlined color="deep-orange"
            class="text-center font-weight-bold"
            @click="toggleMonitoredVuln(item)"
            v-if="item.monitored">Yes</v-chip>
          <v-chip
            small label outlined color="grey"
            class="text-center font-weight-bold"
            @click="toggleMonitoredVuln(item)"
            v-if="!item.monitored">No</v-chip>
        </template>

        <!-- Updated at -->
        <template v-slot:item.updated_at="{ item }">
          <span>{{moment(item.updated_at).format('YYYY-MM-DD, hh:mm')}}</span>
        </template>

      </v-data-table>

      <v-dialog v-model="dialog_vuln" max-width="600px" v-if="this.showManageMetadataButtons()">
        <template v-slot:activator="{ on }">
          <v-btn absolute dark fab bottom left color="deep-orange" v-on="on">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </template>

        <vuln-add-edit></vuln-add-edit>

      </v-dialog>
      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor" dense>
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </v-card>
  </div>
</template>

<script>
import Colors from "../../common/colors";
import Users from "../../common/users";
import FirstSteps from '@/components/pages/FirstSteps.vue';
import VulnAddEdit from '@/components/pages/VulnAddEdit.vue';
import AdvancedSearch from '@/components/pages/AdvancedSearch.vue';
import _ from 'lodash';
import moment from 'moment';

export default {
  name: "vulns",
  mixins: [Colors, Users],
  components: {
    VulnAddEdit, AdvancedSearch
  },
  data: () => ({
    vulns: [],
    loading: true,
    limit: 10,
    search: '',
    search_slider_min: 0,
    search_slider_max: 100,
    showAdvancedFilters: false,
    show_all: true,
    show_last_day: false,
    show_last_week: false,
    options: {},
    headers: [
      { text: 'Score', value: 'score', align: 'center', width: "10%" },
      { text: 'Summary', value: 'summary' },
      { text: 'Metadata', value: 'metadata', align: 'center', width: "8%", sortable: false },
      { text: 'Monitored', value: 'monitored', align: 'center', },
      { text: 'Last update', value: 'updated_at', align: 'center', width: "12%" },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    dialog_vuln: false,
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  watch: {
    search: _.debounce(function (filter) {
      this.search = filter;
      this.options.page = 1;  // reset page count
      this.getDataFromApi();
    }, 500),
    options: {
      handler() {
        this.getDataFromApi();
      },
      deep: true
    },
    search_slider_min: _.debounce(function () {
      this.getDataFromApi();
    }, 500),
    search_slider_max: _.debounce(function () {
      this.getDataFromApi();
    }, 500),
    show_all: {
      handler() {
        this.getDataFromApi();
      },
      deep: true
    },
    show_last_day: {
      handler() {
        this.getDataFromApi();
      },
      deep: true
    },
    show_last_week: {
      handler() {
        this.getDataFromApi();
      },
      deep: true
    },
  },
  methods: {
    getDataFromApi(extra_filters) {
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
        let items = this.getVulns(page, this.limit, sortBy, sortDesc, extra_filters);

        setTimeout(() => {
          resolve({
            items
          });
        }, 300);
      });
      this.loading = false;
    },
    updateAdvancedSearchFilters(filters){
      this.getDataFromApi(filters);
    },
    getVulns(page, itemsPerPage, sortBy, sortDesc, extra_filters) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }

      let filter_by_date = '';
      if (this.show_last_day == true) {
        filter_by_date = "&updated_at__gte=" + moment(new Date()).format('YYYY-MM-DD');
      } else if (this.show_last_week == true) {
        filter_by_date = "&updated_at__gte=" + moment(new Date()).subtract(7 , 'day').format('YYYY-MM-DD');
      }

      if (extra_filters == null || extra_filters == '') {
        extra_filters = "&score__gte="+this.search_slider_min+"&score__lte="+this.search_slider_max
      }

      this.$api.get('/api/vulns/?limit='+itemsPerPage+'&page='+page+'&search='+this.search+'&'+sorted_by+filter_by_date+extra_filters).then(res => {
        this.vulns = res.data;
        this.loading = false;
        return this.vulns;
      }).catch(e => {
        this.vulns = [];
        this.loading = false;
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to get vulns.';
      });
    },
    viewVuln(vuln_id) {
      this.$router.push({ 'name': 'VulnDetails', 'params': { 'vuln_id': vuln_id } });
    },
    editVuln(vuln_id) {
      // Todo
    },
    deleteVuln(vuln_id) {
      // Todo
    },
    clickRow(vulnRow) {
      this.$router.push({ 'name': 'VulnDetails', 'params': { 'vuln_id': vulnRow.id } });
    },
    getBool(b) {
      if (b == true) return 'red';
      else return 'grey';
    },
    toggleShowAll() {
      this.options.page = 1;
      if (this.show_all == false) {
        this.show_all = !this.show_all;
      }
      if (this.show_all == true) {
        this.show_last_day = false;
        this.show_last_week = false;
      }
    },
    toggleShowLastDay() {
      this.options.page = 1;
      if (this.show_last_day == true) {
        this.show_all = true;
        this.show_last_day = false;
        this.show_last_week = false;
      }
      if (this.show_last_day == false) {
        this.show_last_day = true;
        this.show_all = false;
        this.show_last_week = false;
      }
    },
    toggleShowLastWeek() {
      this.options.page = 1;
      if (this.show_last_week == true) {
        this.show_all = true;
        this.show_last_day = false;
        this.show_last_week = false;
      }
      if (this.show_last_week == false) {
        this.show_last_week = true;
        this.show_all = false;
        this.show_last_day = false;
      }
    },
    showManageMetadataButtons(){
      let p = JSON.parse(this.getUserProfile());
      if (p != null && 'manage_metadata' in p){
          return p.manage_metadata;
      } else {
        return true;
      }
    },
    toggleMonitoredVuln(item) {
      // save in backend
      let data = {
        'monitored': !item.monitored,
        'vuln_id': item.id,
        'organization_id': localStorage.getItem('org_id')
      };

      this.$api.put('/api/vulns/'+item.id+'/toggle', data).then(res => {
        if (res){
          item.monitored = !item.monitored;
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Vulnerability monitoring successfuly updated.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to change the vulnerability monitoring status';
        }
      }).catch(e => {
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'Unable to change the vulnerability monitoring status',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
        return;
      });
    },
  }
};
</script>

<style>
.v-data-table td, .v-data-table th {
    padding: 0 8px;
}
.v-dialog {
    position: absolute;
    left: 0;
}
.vendor-chip {
  padding-right: 5px;
  padding-left: 5px;
  margin-right: 3px;
}
.v-chip.v-size--small {
  border-radius: 12px;
  font-size: 12px;
  height: 20px;
}
</style>
