<template>
  <v-container fluid grid-list-md>
    <v-layout row wrap>
      <v-flex md4>
        <v-card color="deep-orange">
          <v-card-title>Vulnerabilities</v-card-title>
          <v-card-subtitle primary>CVE, 0days, ...</v-card-subtitle>
          <v-card-text class="display-3 text-center">
            {{stats.vulns}}
          </v-card-text>
        </v-card>
      </v-flex>
      <v-flex md4>
        <v-card color="lime">
          <v-card-title primary>Metadata</v-card-title>
          <v-card-subtitle primary>Exploits, Threats activities, News, Blog posts</v-card-subtitle>
          <v-card-text class="display-3 text-center">
            {{stats.exploits + stats.threats}}
          </v-card-text>
        </v-card>
      </v-flex>
      <v-flex md4>
        <v-card color="teal">
          <v-card-title primary>Monitored items</v-card-title>
          <v-card-subtitle primary>Vendors, Products, Vulnerabilites, Bulletins</v-card-subtitle>
          <v-card-text class="display-3 text-center">
            {{stats.monitored}}
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>

    <v-layout row wrap>
      <v-flex md12>
        <v-card outlined>
          <v-card-title>Latest monitored vulnerabilities and products (< 30 days)</v-card-title>
          <v-card-text class="text-center">
            <v-data-table
              :headers="monitored_vulns_headers"
              :items="monitored_vulns"
              :items-per-page="5"
              :loading="loading_last_vulns"
              @click:row="viewVuln"
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
                      ><v-icon title="View details" @click="viewVuln(item)">mdi-arrow-right-bold-circle-outline</v-icon>
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
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex md6>
        <v-card outlined>
          <v-card-title>
            Latest vulnerabilities (Top 20)
            <v-chip
              small label outlined color="deep-orange"
              @click="viewVulns()">See all</v-chip>
          </v-card-title>
          <v-card-text class="text-center">
            <v-data-table
              :headers="vulns_headers"
              :items="vulns"
              :items-per-page="5"
              :item-class="rowColor"
              :loading="loading_last_vulns"
              @click:row="viewVuln"
            >
              <template v-slot:item.summary="{ item }">
                <v-clamp autoresize :max-lines="1">
                  {{ item.summary }}
                </v-clamp>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-flex>
      <v-flex md6>
        <v-card outlined>
          <v-card-title primary>Latest exploits metadata (Top 20)</v-card-title>
          <v-card-text class="text-center">
            <v-data-table
              :headers="exploits_headers"
              :items="exploits"
              :items-per-page="5"
              :loading="loading_last_vulns"
            >
              <!-- Relevancy level -->
              <template v-slot:item.relevancy_level="{ item }">
                <!-- <v-icon x-small class="mdi mdi-clock-time-six" color="orange" v-for="n in 5" v-if="item.relevancy_level >= n"></v-icon>
                <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 5" v-if="5-item.relevancy_level >= n"></v-icon> -->

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

              <!-- Link -->
              <template v-slot:item.link="{ item }">
                <v-clamp autoresize :max-lines="1">
                  {{ item.link }}
                </v-clamp>
              </template>

            </v-data-table>
          </v-card-text>
        </v-card>
      </v-flex>
      <!-- <v-flex md4>
        <v-card outlined>
          <v-card-title primary>Latest monitored issues</v-card-title>
          <v-card-text class="display-3 text-center">
            {{stats.monitored}}
          </v-card-text>
        </v-card>
      </v-flex> -->
      <!-- <v-overlay :value="firststeps_overlay" light>
        <v-btn
          icon
          @click="firststeps_overlay = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <first-steps></first-steps>
      </v-overlay> -->
      <v-dialog
        v-model="firststeps_overlay"
        width="600"
      >
        <first-steps></first-steps>
      </v-dialog>
    </v-layout>

  </v-container>
</template>

<script>
import swal from 'sweetalert2';
import VClamp from 'vue-clamp';
import Colors from "../../common/colors";
// import moment from 'moment';
import FirstSteps from '@/components/pages/FirstSteps.vue';

export default {
  name: "Home",
  mixins: [Colors],
  components: {
    VClamp, FirstSteps
  },
  data: () => ({
    stats: {
      'vulns': '...', 'exploits': '...', 'threats': '...', 'monitored': '...',
      'vulns_exploitable': 'n/a'
    },
    vulns: [],
    vulns_headers: [
      { text: 'CVE', value: 'cveid', fixed: true },
      { text: 'Summary', value: 'summary' },
    ],
    monitored_vulns: [],
    monitored_vulns_headers: [
      { text: 'Score', value: 'score', align: 'center', width: "10%" },
      { text: 'Summary', value: 'summary' },
      { text: 'Metadata', value: 'metadata', align: 'center', width: "9%", sortable: false },
      { text: 'Last update', value: 'updated_at', align: 'center', width: "10%" },
    ],
    loading_monitored_vulns: true,
    loading_last_vulns: true,
    exploits: [],
    exploits_headers: [
      { text: 'Relevancy', value: 'relevancy_level', fixed: true },
      { text: 'Link', value: 'link', fixed: true },
    ],
    firststeps: false,
    firststeps_overlay: false
  }),
  watch: {
    firststeps() {
      if (this.firststeps == 1) {
        this.firststeps_overlay = true;
      } else {
        this.firststeps_overlay = false;
      }
    }
  },
  mounted() {
    this.firststeps = this.$route.query.firststeps;
    this.getStats();
    this.getLastVulns();

  },
  methods: {
    async getStats() {
      await this.$api.get('/api/vulns/stats').then(res => {
        if (res && res.status === 200) {
          this.stats = res.data;
          this.loading_last_vulns = false;
        }
      }).catch(e => {
        swal.fire({
          title: 'Error', text: 'Unable to get stats',
          showConfirmButton: false, showCloseButton: false, timer: 3000
        });
      });

    },
    async getLastVulns() {
      await this.$api.get('/api/vulns/latest?timedelta=30').then(res => {
        if (res && res.status === 200) {
          this.vulns = res.data.vulns;
          this.exploits = res.data.exploits;
          this.monitored_vulns = res.data.monitored_vulns;
          this.loading_last_vulns = false;
        }
      }).catch(e => {
        swal.fire({
          title: 'Error', text: 'Unable to get vulnerabilities and exploits',
          showConfirmButton: false, showCloseButton: false, timer: 3000
        });
      });

    },
    viewVuln(item) {
      this.$router.push({ 'name': 'VulnDetails', 'params': { 'vuln_id': item.id } });
    },
    viewVulns() {
      this.$router.push({ 'name': 'Vulns' });
    },
    rowColor(item){
      return this.getRatingColor(item.score);
    }
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
