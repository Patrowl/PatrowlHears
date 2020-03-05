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
            <v-card-subtitle primary>Exploits & Threats activities</v-card-subtitle>
            <v-card-text class="display-3 text-center">
              {{stats.exploits + stats.threats}}
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex md4>
          <v-card color="teal">
            <v-card-title primary>Monitored</v-card-title>
            <v-card-subtitle primary>Vendor / Products</v-card-subtitle>
            <v-card-text class="display-3 text-center">
              {{stats.monitored}}
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>

      <v-layout row wrap>
        <v-flex md12>
          <v-card outlined>
            <v-card-title>Latest Monitored Vulnerabilities</v-card-title>
            <v-card-text class="text-center">
              <v-data-table
                :headers="monitored_vulns_headers"
                :items="monitored_vulns"
                :items-per-page="5"
                @click:row="viewVuln"
              >
                <template v-slot:item.summary="{ item }">
                  <v-clamp autoresize :max-lines="1">
                    {{ item.summary }}
                  </v-clamp>
                </template>

                <template v-slot:item.score="{ item }">
                  <v-chip
                    :color="getRatingColor(item.score)"
                    class="text-center"
                    small
                  >
                  {{item.score}}
                  </v-chip>
                </template>

                <template v-slot:item.is_confirmed="{ item }">
                  <v-icon
                    small
                    class="mdi mdi-check"
                    color="gray"
                    v-if="item.is_confirmed == true"
                  >
                  </v-icon>
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
            <v-card-title>Latest Vulnerabilities</v-card-title>
            <v-card-text class="text-center">
              <v-data-table
                :headers="vulns_headers"
                :items="vulns"
                :items-per-page="5"
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
            <v-card-title primary>Latest exploits</v-card-title>
            <v-card-text class="text-center">
              <v-data-table
                :headers="exploits_headers"
                :items="exploits"
                :items-per-page="5"
              >
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
      </v-layout>
    </v-container>
</template>

<script>
import swal from 'sweetalert2';
import VClamp from 'vue-clamp';
import Colors from "../../common/colors";
import moment from 'moment';

export default {
  name: "Home",
  mixins: [Colors],
  components: {
    VClamp
  },
  data: () => ({
    stats: {
      'vulns': 'n/a', 'exploits': 'n/a', 'threats': 'n/a', 'monitored': 'n/a'
    },
    vulns: [],
    vulns_headers: [
      { text: 'PHID', value: 'id', fixed: true },
      { text: 'CVE', value: 'cve', fixed: true },
      { text: 'Summary', value: 'summary' },
    ],
    monitored_vulns: [],
    monitored_vulns_headers: [
      { text: 'PHID', value: 'id', fixed: true },
      { text: 'CVE', value: 'cve', fixed: true },
      { text: 'Summary', value: 'summary' },
      { text: 'Score', value: 'score' },
      { text: 'Exploits', value: 'exploit_count', align: 'center' },
      { text: 'Confirm ?', value: 'is_confirmed', align: 'center' },
      { text: 'Last update', value: 'updated_at', align: 'center' }
    ],
    exploits: [],
    exploits_headers: [
      { text: 'Source', value: 'source', fixed: true },
      { text: 'Link', value: 'link', fixed: true },
      { text: 'Trust', value: 'trust_level', fixed: true },
    ],
  }),
  mounted() {
    this.getStats();
    this.getLastVulns();
  },
  methods: {
    getStats() {
      this.$api.get('/api/vulns/stats').then(res => {
        if (res && res.status === 200) {
          this.stats = res.data;
        }
      }).catch(e => {
        swal.fire({
          title: 'Error', text: 'Unable to get stats',
          showConfirmButton: false, showCloseButton: false, timer: 3000
        });
      });
    },
    getLastVulns() {
      this.$api.get('/api/vulns/latest?timedelta=30').then(res => {
        if (res && res.status === 200) {
          this.vulns = res.data.vulns;
          this.exploits = res.data.exploits;
          this.monitored_vulns = res.data.monitored_vulns;
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
  }
};
</script>

<style>
/* .trunc {
  background-color: #fff;
  box-shadow: 2px 2px 10px #246756;
  overflow: hidden;
  padding: 2em;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 200px;
} */
</style>
