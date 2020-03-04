<template>
  <div>
    <!-- Vulns Page -->
    <!-- <div class="loading" v-if="loading===true">Loading&#8230;</div> -->

    <v-card>
      <v-card-title>
        <!-- Vulnerabilities -->
        <v-container>
          <v-row>
          <!-- <v-row no-gutters > -->
            <v-col class="pa-2" md="auto">
                Vulnerabilities
            </v-col>
            <v-col class="pa-2">
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
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
              ></v-text-field>

            </v-col>
          </v-row>
        </v-container>
        <!-- <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field> -->
      </v-card-title>

      <v-data-table
        :headers="headers"
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
        <!-- {{ item.summary | truncate(150, '...') }} -->
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
      <!-- <template v-slot:item.rating="{ item }">
        <v-chip
          :color="getRatingColor(item.rating)"
          class="text-center"
          small
        >
        {{item.rating}}
        </v-chip>
      </template> -->
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
      <!-- <template v-slot:item.is_confirmed="{ item }">
        <v-chip
          :color="getBool(item.is_confirmed)"
          class="text-center"
          small
          label
        >
        </v-chip>
      </template> -->
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
        <v-icon
          small
          class="mdi mdi-pencil"
          color="orange"
          @click="editVuln(item)"
        >
        </v-icon>
        <v-icon
          small
          class="mdi mdi-delete"
          color="red"
          @click="deleteVuln(item)"
        >
        </v-icon>
      </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import swal from 'sweetalert2';
import VClamp from 'vue-clamp';
import Colors from "../../common/colors";
import moment from 'moment';

export default {
  name: "vulns",
  mixins: [Colors],
  components: {
    VClamp
  },
  data: () => ({
    vulns: [],
    totalvulns: 0,
    loading: true,
    limit: 20,
    search: '',
    show_all: false,
    show_last_day: true,
    show_last_week: false,
    options: {},
    selected: [],
    headers: [
      { text: 'PHID', value: 'id' },
      { text: 'CVE', value: 'cve', width: '150px' },
      { text: 'Summary', value: 'summary' },
      { text: 'CVSSv2', value: 'cvss', align: 'center' },
      // { text: 'Score', value: 'rating', align: 'center' },
      { text: 'Score', value: 'score', align: 'center' },
      // { text: 'Exploits', value: 'is_exploitable', align: 'center' },
      { text: 'Exploits', value: 'exploit_count', align: 'center' },
      { text: 'Confirm ?', value: 'is_confirmed', align: 'center' },
      { text: 'Last update', value: 'updated_at', align: 'center' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
  }),
  watch: {
    search: {
      handler(filter) {
        this.search = filter;
        this.options.page = 1;  // reset page count
        this.getDataFromApi();
      },
      deep: true
    },
    options: {
      handler() {
        this.getDataFromApi().then(data => {
        });
      },
      deep: true
    },
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
        let items = this.getVulns(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            items
          });
        }, 300);
      });
      this.loading = false;
    },
    getVulns(page, itemsPerPage, sortBy, sortDesc) {
      // this.loading = true;
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

      this.$api.get('/api/vulns/?limit='+itemsPerPage+'&page='+page+'&search='+this.search+'&'+sorted_by+filter_by_date).then(res => {
        this.vulns = res.data;
        this.loading = false;
        return this.vulns;
      }).catch(e => {
        this.vulns = [];
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get vulns',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
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
      if (this.show_all == false) {
        this.show_all = !this.show_all;
      }
      if (this.show_all == true) {
        this.show_last_day = false;
        this.show_last_week = false;
      }
    },
    toggleShowLastDay() {
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
  }
};
</script>

<style>
.v-data-table td, .v-data-table th {
    padding: 0 8px;
}
</style>
