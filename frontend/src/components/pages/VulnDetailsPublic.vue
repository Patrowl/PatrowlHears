<template>
  <v-tabs
    left
    background-color="white"
    color="deep-orange accent-4"
  >
    <v-tab>Summary</v-tab>
    <v-tab>
      <v-badge color="deep-orange" v-if="this.exploits.length > 0" :content="this.exploits.length">Exploits</v-badge>
      <v-badge color="grey" v-if="this.exploits.length == 0" :content="'0'">Exploits</v-badge>
    </v-tab>
    <v-tab>
      <v-badge color="deep-orange"  v-if="this.threats.length > 0" :content="this.threats.length">Threat activities</v-badge>
      <v-badge color="grey"  v-if="this.threats.length == 0" :content="'0'">Threat activities</v-badge>
    </v-tab>

    <!-- Summary -->
    <v-tab-item>
      <v-container fluid grid-list-md>
        <v-layout row wrap>

          <v-flex md9>
            <v-flex>
              <!-- Summary -->
              <v-card color="grey lighten-5">
                <v-card-title primary class="title">
                  <v-container class="grey lighten-5">
                    <v-row no-gutters >
                      <v-col class="pa-2" md="auto">
                          Vuln ID: PH-{{ $route.params.vuln_id }}
                      </v-col>
                      <v-col class="pa-2" md="auto">
                        <v-icon
                          color="deep-orange"
                          title="Download as JSON file"
                          @click="downloadVuln($route.params.vuln_id, 'json')">mdi-download</v-icon>
                        <!-- <v-icon
                          color="deep-orange"
                          title="Send vulnerability as email"
                          @click="dialog_sendmail=true">mdi-email-send-outline</v-icon> -->
                      </v-col>
                      <v-col class="pa-2">
                        <!-- <v-chip
                          small label outlined color="deep-orange"
                          @click="toggleMonitored"
                          v-if="this.vuln.monitored">Monitored</v-chip>
                        <v-chip
                          small label outlined color="grey"
                          @click="toggleMonitored"
                          v-if="!this.vuln.monitored">Not monitored</v-chip> -->
                      </v-col>
                    </v-row>
                  </v-container>
                </v-card-title>
                <v-card-text>
                  <v-list subheader color="grey lighten-5">
                    <v-list-item>
                      <v-list-item-content>
                        <v-list-item-subtitle>CVE</v-list-item-subtitle>
                        {{this.vuln.cveid}}
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item>
                      <v-list-item-content class="d-inline" >
                        <v-list-item-subtitle>CVSSv2</v-list-item-subtitle>
                        <v-chip small label :color="getCVSSColor(this.vuln.cvss)">
                          {{this.vuln.cvss}}
                        </v-chip>
                        -
                        {{this.vuln.cvss_vector}}
                        <!-- ({{moment(this.vuln.cvss_time).format('YYYY-MM-DD')}}) -->
                      </v-list-item-content>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-content class="d-inline" >
                        <v-list-item-subtitle>CVSSv3</v-list-item-subtitle>
                        <v-chip small label :color="getCVSSColor(this.vuln.cvss3)">
                          {{this.vuln.cvss3}}
                        </v-chip>
                        -
                        {{this.vuln.cvss3_vector}}
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item>
                      <v-list-item-content>
                        <v-list-item-subtitle>Summary</v-list-item-subtitle>
                        {{this.vuln.summary}}
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item
                      v-if="this.vuln.cwe_id != ''"
                      :href="'https://cwe.mitre.org/data/definitions/'+this.vuln.cwe_id.replace('CWE-', '')+'.html'"
                      target="_blank"
                      >
                      <v-list-item-content>
                        <v-list-item-subtitle>CWE</v-list-item-subtitle>
                        {{this.vuln.cwe_id}} - {{this.vuln.cwe_name}}
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item
                      v-if="this.vuln.cwe_refs != '' && 'MITRE-ATTACK' in this.vuln.cwe_refs"
                      >
                      <v-list-item-content>
                        <v-list-item-subtitle>Mitre ATT&CK techniques</v-list-item-subtitle>
                        <ul id="v-for-cwe_refs">
                          <li v-for="ref in this.vuln.cwe_refs['MITRE-ATTACK']" link>
                            <a v-bind:href="ref['url']" target="_blank"> {{ ref['external_id'] }} - {{ ref['description']}}</a>
                          </li>
                        </ul>
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item
                      v-if="typeof this.vuln.reflinks !== 'undefined'? this.vuln.reflinks.length > 0: true"
                      >
                      <v-list-item-content>
                        <v-list-item-subtitle>Links</v-list-item-subtitle>
                        <ul id="v-for-reflinks">
                          <li v-for="link in this.vuln.reflinks" :key='link' link>
                            <a v-bind:href="link" target="_blank"> {{ link }} </a>
                          </li>
                        </ul>
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item>
                      <v-list-item-content>
                        <v-list-item-subtitle>Vulnerable product(s) - {{this.vuln.vulnerable_products.length}} CPE</v-list-item-subtitle>
                        <ul id="v-for-cpe">
                          <li v-for="value in this.vuln.vulnerable_products">
                            {{ value }}
                          </li>
                        </ul>
                      </v-list-item-content>
                    </v-list-item>

                    <v-list-item>
                      <v-list-item-content>
                        <v-list-item-subtitle>Vulnerable package(s)</v-list-item-subtitle>
                        <ul id="v-for-package">
                          <template v-for="(value, key) in this.vuln.vulnerable_packages_versions">
                            <template v-for="(subvalue, subkey) in value">
                              <li v-for="(subsubvalue, subsubkey) in subvalue">
                                <v-chip
                                  class="package-chip"
                                  label small
                                >{{ key }}:{{ subkey }} </v-chip> affected: {{ subsubvalue.affected_versions}}, patched: {{ subsubvalue.patched_versions}}

                              </li>
                            </template>
                          </template>
                        </ul>
                      </v-list-item-content>
                    </v-list-item>

                  </v-list>
                </v-card-text>
              </v-card>
            </v-flex>
          </v-flex>

          <!-- Side cards -->
          <v-flex md3>
            <v-flex>
              <v-card
                :color="getRatingColor(vprating)"
                v-if="this.ratings.score >= 0"
                @click="viewRating()"
                >
                <v-card-title class="title">Rating Scores</v-card-title>
                <v-card-text>
                  <v-row justify="center">
                    <span class="display-3 font-weight-bold" >{{vprating}}</span>/100
                  </v-row>
                </v-card-text>
              </v-card>
            </v-flex>
            <v-flex>
              <v-card color="grey lighten-5">
                <v-card-title primary class="title">Metrics</v-card-title>
                <v-card-text>
                  <v-switch
                    v-model="is_exploitable"
                    @click="toggleMetric()"
                    color="deep-orange"
                    readonly
                    hide-details
                    label="Exploitable"
                    style="margin-top: 0px;"></v-switch>
                  <v-switch v-model="is_confirmed" color="deep-orange" readonly hide-details label="Confirmed" style="margin-top: 0px;"></v-switch>
                  <v-switch v-model="is_in_the_news" color="deep-orange" readonly hide-details label="Relayed in the News" style="margin-top: 0px;"></v-switch>
                  <v-switch v-model="is_in_the_wild" color="deep-orange" readonly hide-details label="Exploited in the Wild" style="margin-top: 0px;"></v-switch>
                </v-card-text>
              </v-card>
            </v-flex>

            <v-flex>
              <v-card color="grey lighten-5" height="100%">
                <v-card-title primary class="title">Access</v-card-title>
                <v-card-text>
                  Authentication: <span class="font-weight-bold">{{this.vuln.access.authentication}}</span><br/>
                  Complexity: <span class="font-weight-bold">{{this.vuln.access.complexity}}</span><br/>
                  Vector: <span class="font-weight-bold">{{this.vuln.access.vector}}</span>
                </v-card-text>
              </v-card>
            </v-flex>

            <v-flex>
              <v-card color="grey lighten-5" height="100%">
                <v-card-title primary class="title">Impact</v-card-title>
                <v-card-text>
                  Confidentiality: <span class="font-weight-bold">{{this.vuln.impact.confidentiality}}</span><br/>
                  Integrity: <span class="font-weight-bold">{{this.vuln.impact.integrity}}</span><br/>
                  Availability: <span class="font-weight-bold">{{this.vuln.impact.availability}}</span>
                </v-card-text>
              </v-card>
            </v-flex>

          </v-flex>
        </v-layout>
        <v-snackbar v-model="snack" :timeout="3000" :color="snackColor" dense>
          {{ snackText }}
          <v-btn text @click="snack = false">Close</v-btn>
        </v-snackbar>
      </v-container>

      <!-- <v-dialog v-model="dialog_sendmail" max-width="600px">
        <v-card>
          <v-card-title>
            <span class="headline">Send vulnerability by email</span>
          </v-card-title>
          <v-card-text>
            <v-form ref="form-vuln-sendmail">
              <v-row>
                <v-textarea
                  v-model="notification_data.emails"
                  rows="3"
                  label="Emails"
                  hint="Email addresses separated with comma or 1 per line. 10 emails max"
                  prepend-icon="mdi-email"
                  ></v-textarea>
              </v-row>
              <v-btn color="success" @click="sendEmailVuln($route.params.vuln_id)">Send</v-btn>
              <v-btn color="warning" type="reset">Reset</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-dialog> -->
    </v-tab-item>

    <!-- Exploits -->
    <v-tab-item>
      <v-card color="grey lighten-5">
        <v-data-table
          :headers="exploit_headers"
          :items="exploits"
          class="elevation-4"
          item-key="link"
          multi-sort
          show-expand
          :expanded.sync="expanded"
        >
          <!-- Scope -->
          <template v-slot:item.scope="{ item }">
            <v-icon
              v-if='item.scope=="public"'
              color="green"
              >mdi-lock-open-variant</v-icon>
            <v-icon
              v-else
              color="orange darken-2"
              >mdi-lock</v-icon>
          </template>

          <!-- Link -->
          <template v-slot:item.link="{ item }">
            <a :href="item.link" target="_blank">{{ item.link }}</a>
          </template>

          <!-- Relevancy level -->
          <template v-slot:item.relevancy_level="{ item }">
            <v-icon x-small class="mdi mdi-clock-time-six" color="yellow" v-for="n in 1" :key='n' v-if="item.relevancy_level == 1"></v-icon>
            <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 4" :key='n' v-if="item.relevancy_level == 1"></v-icon>

            <v-icon x-small class="mdi mdi-clock-time-six" color="orange" v-for="n in 2" :key='n' v-if="item.relevancy_level == 2"></v-icon>
            <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 3" :key='n' v-if="item.relevancy_level == 2"></v-icon>

            <v-icon x-small class="mdi mdi-clock-time-six" color="orange darken-4" v-for="n in 3" :key='n' v-if="item.relevancy_level == 3"></v-icon>
            <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 2" :key='n' v-if="item.relevancy_level == 3"></v-icon>

            <v-icon x-small class="mdi mdi-clock-time-six" color="red" v-for="n in 4" :key='n' v-if="item.relevancy_level == 4"></v-icon>
            <v-icon x-small class="mdi mdi-clock-time-six-outline" color="grey" v-for="n in 1" :key='n' v-if="item.relevancy_level == 4"></v-icon>

            <v-icon x-small class="mdi mdi-clock-time-six" color="red darken-4" v-for="n in 5" :key='n' v-if="item.relevancy_level == 5"></v-icon>
          </template>

          <!-- Trust level -->
          <template v-slot:item.trust_level="{ item }">
            {{ item.trust_level | capitalize }}
          </template>

          <!-- TLP -->
          <template v-slot:item.tlp_level="{ item }">
            <v-chip class="ma-2" label outlined small :color="getTLPColor(item.tlp_level)">
              {{ item.tlp_level | capitalize }}
            </v-chip>
          </template>

          <!-- Updated at -->
          <template v-slot:item.modified="{ item }">
            <span>{{ moment(item.modified).format('YYYY-MM-DD') }}</span>
          </template>

          <!-- Expand -->
          <template v-slot:expanded-item="{ headers, item }">
            <td :colspan="headers.length">{{ item.notes }}</td>
          </template>
        </v-data-table>

      </v-card>
      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </v-tab-item>

    <!-- Activities -->
    <v-tab-item>
      <v-card>
        <v-data-table
          :headers="threat_headers"
          :items="threats"
          class="elevation-4"
          item-key="id"
          multi-sort
          show-expand
          :expanded.sync="expanded"
        >
          <!-- Scope -->
          <template v-slot:item.scope="{ item }">
            <v-icon
              v-if='item.scope=="public"'
              color="green"
              >mdi-lock-open-variant</v-icon>
            <v-icon
              v-else
              color="orange darken-2"
              >mdi-lock</v-icon>
          </template>

          <!-- Link -->
          <template v-slot:item.link="{ item }">
            <a :href="item.link" target="_blank">{{ item.link }}</a>
          </template>

          <!-- Trust level -->
          <template v-slot:item.trust_level="{ item }">
            {{ item.trust_level | capitalize }}
          </template>

          <!-- TLP -->
          <template v-slot:item.tlp_level="{ item }">
            <v-chip class="ma-2" label outlined small :color="getTLPColor(item.tlp_level)">
              {{ item.tlp_level | capitalize }}
            </v-chip>
          </template>

          <!-- Updated at -->
          <template v-slot:item.modified="{ item }">
            <span>{{ moment(item.modified).format('YYYY-MM-DD') }}</span>
          </template>

          <!-- Expand -->
          <template v-slot:expanded-item="{ headers, item }">
            <td :colspan="headers.length">{{ item.notes }}</td>
          </template>

        </v-data-table>

      </v-card>
      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </v-tab-item>
  </v-tabs>

</template>

<script>
import swal from 'sweetalert2';
import moment from 'moment';
import router from '../../router';
import Users from "../../common/users";
import Colors from "../../common/colors";
import Download from "../../common/download";
import DialogVulnAddEdit from '@/components/vulnerability/vulnerabilityDetails/dialog/DialogVulnAddEdit.vue';

export default {
  name: 'VulnDetailsPublic',
  mixins: [Users, Colors, Download],
  components: {
    DialogVulnAddEdit
  },
  data: () => ({
    expanded: [],
    vuln_id: "",
    vuln: {
      cwe_id: 'UNKWNOWN',
      cwe_refs: {},
      impact: {confidentiality: '', integrity: '', availability: ''},
      access: {authentication: '', complexity: '', vector: ''},
      reflinks: [],
      vulnerable_products: [],
    },
    ratings: {
      score: 0,
      cvssv2adj: 0
    },
    threats: [],
    threat_headers: [
      { text: 'Scope', value: 'scope' },
      { text: 'Link', value: 'link' },
      { text: 'Trust level', value: 'trust_level' },
      { text: 'TLP', value: 'tlp_level', align: 'center' },
      { text: 'Source', value: 'source', align: 'center' },
      { text: 'In the Wild ?', value: 'is_in_the_wild', align: 'center' },
      { text: 'In the News ?', value: 'is_in_the_news', align: 'center' },
      { text: 'Last update', value: 'modified', align: 'center' },
      // { text: 'Actions', value: 'action', sortable: false },
      // { text: '', value: 'data-table-expand' },
    ],
    exploits: [],
    exploit_headers: [
      { text: 'Scope', value: 'scope' },
      { text: 'Link', value: 'link' },
      { text: 'TLP', value: 'tlp_level', align: 'center' },
      { text: 'Relevancy', value: 'relevancy_level' },
      { text: 'Trust', value: 'trust_level' },
      { text: 'Source', value: 'source', align: 'center' },
      // { text: 'Availability', value: 'availability', align: 'center' },
      // { text: 'Maturity', value: 'maturity', align: 'center' },
      { text: 'Last update', value: 'modified', align: 'center' },
      // { text: 'Actions', value: 'action', sortable: false },
      { text: '', value: 'data-table-expand' },
    ],
    editedIndex: -1,
    editedItem: {},
    dialog_sendmail: false,
    notification_data: {
      'emails': ''
    },
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  beforeRouteUpdate(to) {
    this.vuln_id = to.params.vuln_id;
  },
  mounted() {
    this.vuln_id = this.$router.currentRoute.params.vuln_id;
    this.editedItem = this.defaultMetadata;
    this.getDataFromApi(this.vuln_id);
  },
  computed: {
    is_exploitable(){
      return this.vuln.is_exploitable;
    },
    is_confirmed(){
      return this.vuln.is_confirmed;
    },
    is_in_the_news(){
      return this.vuln.is_in_the_news;
    },
    is_in_the_wild(){
      return this.vuln.is_in_the_wild;
    },
    vprating(){
      return this.vuln.score;
    },
    cvssv2adj(){
      return this.ratings.cvssv2adj;
    },
    vuln_vector(){
      let vector = "";

      // Vulnerability
      vector += this.vuln.cvss_vector;
      this.vuln.is_confirmed ? vector += "/CL:Y":null;
      if (moment(this.vuln.published).isValid()) {
        vector += "/VX:" + moment().diff(moment(this.vuln.published), 'days');
      }

      // Exploits/Threats
      let ea_metrics = ['unknown', 'private', 'public'];
      let ea_vectors = ['X', 'R', 'U'];
      let em_metrics = ['unknown', 'unproven', 'poc', 'functional'];
      let em_vectors = ['X', 'U', 'P', 'F'];
      let et_metrics = ['unknown', 'low', 'medium', 'high', 'trusted'];
      let et_vectors = ['X', 'L', 'M', 'H', 'H'];
      let ea_idx, ea_max_idx = 0;
      let em_idx, em_max_idx = 0;
      let et_idx, et_max_idx = 0;
      let ex_max_days = 0;
      for (let i = 0; i < this.exploits.length; i++){
        ea_idx = ea_metrics.indexOf(this.exploits[i].availability)
        ea_idx > ea_max_idx ? ea_max_idx = ea_idx:null;
        em_idx = em_metrics.indexOf(this.exploits[i].maturity)
        em_idx > em_max_idx ? em_max_idx = em_idx:null;
        et_idx = et_metrics.indexOf(this.exploits[i].trust_level)
        et_idx > et_max_idx ? et_max_idx = et_idx:null;
        if (moment(this.exploits[i].published).isValid()) {
          if (moment().diff(moment(this.exploits[i].published), 'days') > ex_max_days) {
            ex_max_days = moment().diff(moment(this.exploits[i].published), 'days');
          }
        }
      }
      vector += "/EA:" + ea_vectors[ea_max_idx];
      vector += "/EM:" + em_vectors[em_max_idx];
      vector += "/ET:" + et_vectors[et_max_idx];
      vector += "/EX:" + ex_max_days;
      this.is_in_the_news ? vector += "/N:Y":null;
      this.is_in_the_wild ? vector += "/W:Y":null;

      return vector;
    }
  },
  methods: {
    getDataFromApi(vuln_id) {
      return new Promise((resolve, reject) => {
        let vuln = this.getVulnDetails(vuln_id);
        let exploits = this.getExploits(vuln_id);
        let threats = this.getThreats(vuln_id);

        setTimeout(() => {
          this.loading = false;
          resolve({ vuln, exploits, threats });
        }, 300);
      });
    },
    getVulnDetails(vuln_id) {
      this.loading = true;
      this.$api.get('/api/public/vulns/'+vuln_id+'/').then(res => {
        this.vuln = res.data;
        return this.vuln;
      }).catch(e => {
        this.vuln = {};
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get vuln details',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading = false;
    },
    getExploits(vuln_id) {
      this.loading = true;
      this.$api.get('/api/public/vulns/'+vuln_id+'/exploits').then(res => {
        if (res && res.status === 200) {
          this.exploits = res.data;
        }
        return this.exploits;
      }).catch(e => {
        this.exploits = {};
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get related exploits',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading = false;
    },
    getThreats(vuln_id) {
      this.loading = true;
      this.$api.get('/api/public/vulns/'+vuln_id+'/threats').then(res => {
        // this.threats = res.data;
        if (res && res.status === 200) {
          this.threats = res.data;
        }
        return this.threats;
      }).catch(e => {
        this.threats = {};
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get related threats',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading = false;
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
    // sendEmailVuln(vuln_id) {
    //   this.$api.post('/api/public/vulns/'+vuln_id+'/export/email', this.notification_data).then(res => {
    //     this.snack = true;
    //     this.snackColor = 'success';
    //     this.snackText = 'Vulnerability details successfuly sent by mail.';
    //   }).catch(e => {
    //     this.snack = true;
    //     this.snackColor = 'error';
    //     this.snackText = 'Unable to send vulnerability details.';
    //   });
    //   this.dialog_sendmail = false;
    // },
    loadExploit(item) {
      this.editedIndex = this.exploits.indexOf(item);
      this.editedItem = Object.assign({}, this.defaultMetadata);
      this.editedItem.id = item.id;
      this.editedItem.availability = item.availability;
      this.editedItem.link = item.link;
      this.editedItem.maturity = item.maturity;
      this.editedItem.notes = item.notes;
      this.editedItem.source = item.source;
      this.editedItem.tlp_level = item.tlp_level;
      this.editedItem.trust_level = item.trust_level;
      this.dialog_exploit = true;
    },
    loadThreat(item) {
      this.editedIndex = this.threats.indexOf(item);
      this.editedItem = Object.assign({}, this.defaultMetadata);
      this.editedItem.id = item.id;
      this.editedItem.link = item.link;
      this.editedItem.notes = item.notes;
      this.editedItem.source = item.source;
      this.editedItem.tlp_level = item.tlp_level;
      this.editedItem.trust_level = item.trust_level;
      this.editedItem.is_in_the_news = item.is_in_the_news == false?0:1;
      this.editedItem.is_in_the_wild = item.is_in_the_wild == false?0:1;
      this.dialog_threat = true;
    },
    viewRating() {
      this.$router.push({ 'name': 'Ratings', 'query': { 'vector': this.vuln_vector } });
    },
    toggleMetric(item) {
      this.snack = true;
      this.snackColor = 'error';
      this.snackText = 'Unable to change the metrics - Insufficient privileges';
    },
  }
}
</script>

<style>
.inactive {
  opacity: .5;
}

.invert {
  padding: .5em 0;
  color: white;
  background-color: black;
}

.package-chip {
  padding-right: 5px;
  padding-left: 5px;
  margin-right: 3px;
}
</style>
