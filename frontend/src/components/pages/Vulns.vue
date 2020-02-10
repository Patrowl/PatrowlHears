<template>
  <div>
    <!-- Vulns Page -->
    <div class="loading" v-if="loading===true">Loading&#8230;</div>
    <v-card>
      <v-card-title>
        Vulnerabilities
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
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
        <v-chip
          :color="getBool(item.is_confirmed)"
          class="text-center"
          small
          label
        >
        </v-chip>
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


export default {
  name: "vulns",
  components: {
    VClamp
  },
  data: () => ({
    vulns: [],
    totalvulns: 0,
    loading: true,
    limit: 20,
    search: '',
    options: {},
    selected: [],
    headers: [
      { text: 'PHID', value: 'id' },
      { text: 'CVE', value: 'cve', width: '150px' },
      { text: 'Summary', value: 'summary' },
      { text: 'CVSSv2', value: 'cvss', align: 'center' },
      // { text: 'Exploits', value: 'is_exploitable', align: 'center' },
      { text: 'Exploits', value: 'exploit_count', align: 'center' },
      { text: 'Confirm ?', value: 'is_confirmed', align: 'center' },
      { text: 'Last update', value: 'updated_at', align: 'center' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
  }),
  mounted() {
    // nothing yet
  },
  // computed: {
  //   formatdate(){
  //     return Vue.filter('date')(this.value)
  //   }
  // },
  watch: {
    search: {
      handler(filter) {
        this.search = filter;
        this.options.page = 1;  // reset page count
        this.getDataFromApi().then(data => {
          // this.vulns = data.results;
          // this.totalvulns = data.count;
        });
      },
      deep: true
    },
    options: {
      handler() {
        this.getDataFromApi().then(data => {
          // this.vulns = data.results;
          // this.totalvulns = data.count;
        });
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
        let search = this.search.trim().toLowerCase();

        this.limit = itemsPerPage;
        let items = this.getvulns(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          this.loading = false;
          resolve({
            items
          });
        }, 300);
      });
    },
    getvulns(page, itemsPerPage, sortBy, sortDesc) {
      this.loading = true;
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }

      this.$api.get('/api/vulns/?limit='+itemsPerPage+'&page='+page+'&search='+this.search+'&'+sorted_by).then(res => {
        this.vulns = res.data;
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
      this.loading = false;
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
    getColor(criticity) {
      if (criticity == 'info') return 'blue';
      else if (criticity == 'low') return 'yellow';
      else if (criticity == 'medium') return 'orange';
      else if (criticity == 'high') return 'red';
      else return 'grey';
    },
    getBool(b) {
      if (b == true) return 'red';
      else return 'grey';
    },
  }
};
</script>
