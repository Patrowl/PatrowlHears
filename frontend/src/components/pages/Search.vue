<template>
  <div>
    Search page - Results for {{this.appsearch}}
    <v-progress-circular
      indeterminate
      rotate="0"
      size="24"
      width="4"
      color="deep-orange"
      v-if="loading===true"
    ></v-progress-circular>

    <v-container fluid>
      <v-row dense>
        <v-col
          v-for="result in results"
          :key="result.type+result.value.id"
          cols="4"
        >
    <v-card>
      <v-card-title v-if="result.type == 'vuln'">
        Vulnerability #PHID-{{result.value.id}}
      </v-card-title>
      <v-card-subtitle v-if="result.type == 'vuln'">
        <v-clamp autoresize :max-lines="3">
          {{result.value.summary}}
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
      </v-card-subtitle>
      <v-card-text v-if="result.type == 'vuln'">
        <dl>
          <dt>Score</dt>
          <dd><v-chip small label :color="getRatingColor(result.value.score)" class="pa-2">
            {{result.value.score}}
          </v-chip></dd>
          <dt>CVE</dt><dd>{{result.value.cve_id}}</dd>
          <dt>CVSSv2</dt>
          <!-- <dd><v-chip small label :color="getCVSSColor(result.value.cvss)" class="pa-2">
            {{result.value.cvss}}
          </v-chip></dd> -->
          <dd>{{result.value.cvss}} - {{result.value.cvss_vector}}</dd>
          <dt>Products</dt><dd>{{getVendorProduct(result.value.vulnerable_products)}}</dd>
          <dt>Last update</dt><dd>{{ moment(result.value.updated_at).format('YYYY-MM-DD') }}</dd>
        </dl>
        <v-chip
          outlined class="pa-2" style="height: 20px;"
          :color="getBoolColor(result.value.is_exploitable)">
          Exploitable: {{getBoolValue(result.value.is_exploitable)}}
        </v-chip>&nbsp;
        <v-chip
          outlined class="pa-2" style="height: 20px;"
          :color="getBoolColor(result.value.is_confirmed)">
          Confirmed: {{getBoolValue(result.value.is_confirmed)}}
        </v-chip>&nbsp;
        <v-chip
          outlined class="pa-2" style="height: 20px;"
          :color="getBoolColor(result.value.is_in_the_news)">
          In the news: {{getBoolValue(result.value.is_in_the_news)}}
        </v-chip>&nbsp;
        <v-chip
          outlined class="pa-2" style="height: 20px;"
          :color="getBoolColor(result.value.is_in_the_wild)">
          In the wild: {{getBoolValue(result.value.is_in_the_wild)}}
        </v-chip>
      </v-card-text>

      <v-card-title v-if="result.type == 'exploit'">
        Exploit for #PHID-{{result.value.vuln}}
      </v-card-title>
      <v-card-subtitle v-if="result.type == 'exploit'">
        {{result.value.link}}
      </v-card-subtitle>
      <v-card-text v-if="result.type == 'exploit'">
        <dl>
          <dt>Trust Level</dt><dd>{{result.value.trust_level | capitalize}}</dd>
          <dt>TLP</dt><dd>{{result.value.tlp_level | capitalize}}</dd>
          <dt>Source</dt><dd>{{result.value.source | capitalize}}</dd>
          <dt>Availability</dt><dd>{{result.value.availability | capitalize}}</dd>
          <dt>Maturity</dt><dd>{{result.value.maturity | capitalize}}</dd>
          <dt>Notes</dt>
          <dd>
            <v-clamp autoresize :max-lines="5">
              {{result.value.notes}}
              <button
                v-if="expanded || clamped"
                slot="after"
                slot-scope="{ toggle, expanded, clamped }"

                @click="toggle"
              >
                {{ ' more' }}
              </button>
            </v-clamp>
          </dd>
          <dt>Last update</dt><dd>{{ moment(result.value.modified).format('YYYY-MM-DD') }}</dd>
        </dl>
      </v-card-text>

      <v-card-actions>
        <v-btn
        text color="deep-orange accent-4"
        :to="'/vulns/'+result.value.vuln"
        v-if="result.type == 'exploit'"
        >Explore</v-btn>
        <v-btn
        text color="deep-orange accent-4"
        :to="'/vulns/'+result.value.id"
        v-if="result.type == 'vuln'"
        >Explore</v-btn>
        <!-- <v-btn text color="deep-gray accent-4">Bookmark</v-btn>
        <v-spacer></v-spacer>
        <v-btn icon>
          <v-icon>mdi-heart</v-icon>
        </v-btn>
        <v-btn icon>
          <v-icon>mdi-share-variant</v-icon>
        </v-btn> -->
      </v-card-actions>
    </v-card>
  </v-col>
    </v-row>
    </v-container>
  </div>
</template>

<script>
import router from "../../router";
import VClamp from 'vue-clamp';
import Colors from "../../common/colors";

export default {
  name: "Search",
  mixins: [Colors],
  components: {
    VClamp
  },
  data: () => ({
    results: [],
    totalresults: 0,
    loading: true,
    limit: 25,
    options: {},
    appsearch: '',
    // appsearch: this.$route.params.appsearch
  }),
  beforeRouteUpdate(to) {
    this.appsearch = to.params.appsearch
  },
  mounted() {
    this.appsearch = this.$router.currentRoute.params.appsearch;
  },
  watch: {
    appsearch: {
      handler(filter) {
        this.appsearch = filter;
        this.getDataFromApi();
      }
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
        // let search = this.search.trim().toLowerCase();

        this.limit = itemsPerPage;
        let items = this.search_query(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            items
          });
        }, 300);
      });
      this.loading = false;
    },
    search_query(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      // if (sortBy.length > 0) {
      //   if (sortDesc[0] === true) {
      //     sorted_by = '&sorted_by=-' + sortBy;
      //   } else {
      //     sorted_by = '&sorted_by=' + sortBy;
      //   }
      // }
      let search = this.appsearch.trim().toLowerCase();
      this.$api.get('/api/search/'+search+'?limit='+itemsPerPage+'&page='+page+sorted_by).then(res => {
        this.results = res.data;
        this.loading = false;
        return this.vulns;
      }).catch(e => {
        this.results = [];
        // this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get results from search query',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
    },
    getBoolValue(b) {
      return b?'Yes':'No';
    },
    getVendorProduct(cpes) {
      // console.log(cpes);
      var cpe, vp;
      var vp_list = Array();
      var res = "";
      for (cpe of cpes) {
        vp = cpe.split(":")[4].replace(/_/g, ' ') + ' ('+ cpe.split(":")[3].replace(/_/g, ' ') +')';
        vp_list.push(vp);
      }
      vp_list = [...new Set(vp_list)];
      return vp_list.join(', ');
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
