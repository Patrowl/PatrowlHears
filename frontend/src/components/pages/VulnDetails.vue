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
    <v-tab>Timeline</v-tab>

    <!-- Summary -->
    <v-tab-item>
      <v-container fluid grid-list-md>
        <v-layout row wrap>

          <v-flex md8>
            <!-- Summary -->
            <v-card color="grey lighten-5">
              <v-card-title primary class="title">
                <v-container class="grey lighten-5">
                  <v-row no-gutters >
                    <v-col class="pa-2" md="auto">
                        Vuln ID: PH-{{ $route.params.vuln_id }}
                    </v-col>
                    <v-col class="pa-2">
                      <v-chip
                        small label outlined color="deep-orange"
                        @click="toggleMonitored"
                        v-if="this.vuln.monitored">Monitored</v-chip>
                      <v-chip
                        small label outlined color="grey"
                        @click="toggleMonitored"
                        v-if="!this.vuln.monitored">Not monitored</v-chip>
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
                        ({{moment(this.vuln.cvss_time).format('YYYY-MM-DD')}})
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
                    :href="'https://cwe.mitre.org/data/definitions/'+this.vuln.cwe_id+'.html'"
                    >
                    <v-list-item-content>
                      <v-list-item-subtitle>CWE</v-list-item-subtitle>
                      CWE-{{this.vuln.cwe_id}}
                    </v-list-item-content>
                  </v-list-item>

                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Links</v-list-item-subtitle>
                      <ul id="v-for-reflinks">
                        <li v-for="link in this.vuln.reflinks" link>
                          <a v-bind:href="link"> {{ link }} </a>
                        </li>
                      </ul>
                    </v-list-item-content>
                  </v-list-item>

                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Vulnerable products (CPE)</v-list-item-subtitle>
                      <ul id="v-for-cpe">
                        <li v-for="value in this.vuln.vulnerable_products">
                          {{ value }}
                        </li>
                      </ul>
                    </v-list-item-content>
                  </v-list-item>

                </v-list>
              </v-card-text>
            </v-card>
          </v-flex>

          <!-- Side cards -->
          <v-flex md4>
            <v-flex>
              <!-- <v-card color="red lighten-1"> -->
              <v-card
                :color="getRatingColor(vprating)"
                v-if="this.ratings.score >= 0"
                @click="viewRating()"
                >
                <v-card-title class="title">Rating Scores</v-card-title>
                <v-card-text>
                  <v-row align="center">
                    <v-col class="display-3 font-weight-bold" cols="4" align="center" justify="center">
                      {{vprating}}
                    </v-col>
                    <!-- <v-col cols="6">
                      CVSSv2 Base: <span class="font-weight-bold">{{cvssv2adj[0]}}</span><br/>
                      CVSSv2 Temporal: <span class="font-weight-bold">{{cvssv2adj[1]}}</span>
                    </v-col> -->
                  </v-row>
                </v-card-text>
              </v-card>
            </v-flex>
            <v-flex>
              <v-card color="grey lighten-5">
                <v-card-title primary class="title">Metrics</v-card-title>
                <v-card-text>
                  <v-switch v-model="is_exploitable" color="deep-orange" readonly hide-details label="Exploitable" style="margin-top: 0px;"></v-switch>
                  <v-switch v-model="is_confirmed" color="deep-orange" readonly hide-details label="Confirmed" style="margin-top: 0px;"></v-switch>
                  <v-switch v-model="is_in_the_news" color="deep-orange" readonly hide-details label="Relayed in the News" style="margin-top: 0px;"></v-switch>
                  <v-switch v-model="is_in_the_wild" color="deep-orange" readonly hide-details label="Exploited in the Wild" style="margin-top: 0px;"></v-switch>
                </v-card-text>
              </v-card>
            </v-flex>

            <v-flex>
              <v-row no-gutters>
                <v-col cols="12" sm="6">
                  <v-card color="grey lighten-5" height="100%">
                    <v-card-title primary class="title">Impact</v-card-title>
                    <v-card-text>
                      Confidentiality: <span class="font-weight-bold">{{this.vuln.impact.confidentiality}}</span><br/>
                      Integrity: <span class="font-weight-bold">{{this.vuln.impact.integrity}}</span><br/>
                      Availability: <span class="font-weight-bold">{{this.vuln.impact.availability}}</span>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-card color="grey lighten-5" height="100%">
                    <v-card-title primary class="title">Access</v-card-title>
                    <v-card-text>
                      Authentication: <span class="font-weight-bold">{{this.vuln.access.authentication}}</span><br/>
                      Complexity: <span class="font-weight-bold">{{this.vuln.access.complexity}}</span><br/>
                      Vector: <span class="font-weight-bold">{{this.vuln.access.vector}}</span>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-flex>
            <!-- <v-flex>
              <v-card color="grey lighten-5">
                <v-card-title primary class="title">Drop Zone</v-card-title>
                <v-card-text>
                  <drop class="drop" @drop="handleDrop">Dropzone</drop>
                </v-card-text>
              </v-card>
            </v-flex> -->
          </v-flex>
        </v-layout>
      </v-container>
    </v-tab-item>

    <!-- Exploits -->
    <v-tab-item>
      <v-card color="grey lighten-5">
        <v-data-table
          :headers="exploit_headers"
          :items="exploits"
          class="elevation-4"
          item-key="id"
          multi-sort
          show-expand
          :expanded.sync="expanded"
        >
          <!-- Link -->
          <template v-slot:item.link="{ item }">
            <a :href="item.link">{{ item.link }}</a>
          </template>

          <!-- Trus level -->
          <template v-slot:item.trust_level="{ item }">
            {{ item.trust_level | capitalize }}
          </template>

          <!-- TLP -->
          <template v-slot:item.tlp_level="{ item }">
            <v-chip class="ma-2" label outlined small :color="getTLPColor(item.tlp_level)">
              TLP:{{ item.tlp_level | capitalize }}
            </v-chip>
          </template>

          <!-- Updated at -->
          <template v-slot:item.modified="{ item }">
            <span>{{ moment(item.modified).format('YYYY-MM-DD') }}</span>
          </template>

          <!-- Actions -->
          <template v-slot:item.action="{ item }">
            <v-icon small class="mdi mdi-pencil" color="orange" @click="editExploit(item)"></v-icon>
            <v-icon small class="mdi mdi-delete" color="red" @click="deleteExploit(item)"></v-icon>
          </template>

          <!-- Expand -->
          <template v-slot:expanded-item="{ headers, item }">
            <td :colspan="headers.length">{{ item.notes }}</td>
          </template>
        </v-data-table>

        <v-dialog v-model="dialog_exploit" max-width="500px">
          <template v-slot:activator="{ on }">
            <v-btn absolute dark fab bottom left color="deep-orange" v-on="on">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <v-card>
            <v-card-title>
              <span class="headline">{{ formExploitTitle }}</span>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-form ref="form-new-exploit">
                  <v-text-field v-model="editedItem.link" label="link"></v-text-field>
                  <v-select v-model="editedItem.trust_level" label="Trust Level" :items="editedItem.trust_level_items"></v-select>
                  <v-select v-model="editedItem.tlp_level" label="TLP Level" :items="editedItem.tlp_level_items"></v-select>
                  <v-text-field v-model="editedItem.source" label="Source"></v-text-field>
                  <v-select v-model="editedItem.availability" label="Availability" :items="editedItem.availability_items"></v-select>
                  <v-select v-model="editedItem.maturity" label="Maturity" :items="editedItem.maturity_items"></v-select>
                  <v-text-field v-model="editedItem.notes" label="Notes"></v-text-field>

                  <v-btn color="success" @click="saveNewExploit">Save</v-btn>
                  <v-btn color="warning" type="reset">Reset</v-btn>
                </v-form>
              </v-container>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <!-- <v-btn color="blue darken-1" text @click="close">Cancel</v-btn> -->
              <!-- <v-btn color="blue darken-1" text @click="save">Save</v-btn> -->
            </v-card-actions>
          </v-card>
        </v-dialog>

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
          <!-- Link -->
          <template v-slot:item.link="{ item }">
            <a :href="item.link">{{ item.link }}</a>
          </template>

          <!-- Trus level -->
          <template v-slot:item.trust_level="{ item }">
            {{ item.trust_level | capitalize }}
          </template>

          <!-- TLP -->
          <template v-slot:item.tlp_level="{ item }">
            <v-chip class="ma-2" label outlined small :color="getTLPColor(item.tlp_level)">
              TLP:{{ item.tlp_level | capitalize }}
            </v-chip>
          </template>

          <!-- Updated at -->
          <template v-slot:item.modified="{ item }">
            <span>{{ moment(item.modified).format('YYYY-MM-DD') }}</span>
          </template>

          <!-- Actions -->
          <template v-slot:item.action="{ item }">
            <v-icon small class="mdi mdi-pencil" color="orange" @click="editThreat(item)"></v-icon>
            <v-icon small class="mdi mdi-delete" color="red" @click="deleteThreat(item)"></v-icon>
          </template>

          <!-- Expand -->
          <template v-slot:expanded-item="{ headers, item }">
            <td :colspan="headers.length">{{ item.notes }}</td>
          </template>

        </v-data-table>

        <v-dialog v-model="dialog_threat" max-width="500px">
          <template v-slot:activator="{ on }">
            <v-btn absolute dark fab bottom left color="deep-orange" v-on="on">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <v-card>
            <v-card-title>
              <span class="headline">{{ formThreatTitle }}</span>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-form ref="form-new-threat">
                  <v-text-field v-model="editedItem.link" label="link"></v-text-field>
                  <v-select v-model="editedItem.trust_level" label="Trust Level" :items="editedItem.trust_level_items"></v-select>
                  <v-select v-model="editedItem.tlp_level" label="TLP Level" :items="editedItem.tlp_level_items"></v-select>
                  <v-text-field v-model="editedItem.source" label="Source"></v-text-field>
                  <v-select v-model="editedItem.availability" label="Availability" :items="editedItem.availability_items"></v-select>
                  <v-select v-model="editedItem.maturity" label="Maturity" :items="editedItem.maturity_items"></v-select>
                  <v-text-field v-model="editedItem.notes" label="Notes"></v-text-field>
                  <v-btn color="success" @click="saveNewThreat">Save</v-btn>
                </v-form>
              </v-container>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <!-- <v-btn color="blue darken-1" text @click="close">Cancel</v-btn> -->
              <!-- <v-btn color="blue darken-1" text @click="save">Save</v-btn> -->
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-card>
      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </v-tab-item>

    <!-- Timeline -->
    <v-tab-item>
      <v-card v-if="this.history" color="grey lighten-5">
        <!-- {{this.history}} -->
        <v-timeline v-if="this.history.length > 0" clipped dense>
          <v-timeline-item
            v-for="change in this.history"
            :key="change.date"
            color="blue"
            small
            fill-dot
          >
            <v-card class="elevation-2">
              <v-card-title class="headline">{{change.reason}} at '{{change.date}}'</v-card-title>
              <v-card-text>
                <span v-for="c in change.changes" :key="c">{{c}}<br/></span>
              </v-card-text>
            </v-card>
          </v-timeline-item>
        </v-timeline>
      </v-card>
    </v-tab-item>
  </v-tabs>



</template>

<script>
import axios from 'axios';
import swal from 'sweetalert2';
import router from '../../router';
import moment from 'moment';

export default {
  name: 'VulnDetails',
  data: () => ({
    expanded: [],
    vuln_id: "",
    vuln: {
      cwe_id: '',
      impact: {confidentiality: '', integrity: '', availability: ''},
      access: {authentication: '', complexity: '', vector: ''},
    },
    ratings: {},
    history: {},
    threats: {},
    threat_headers: [
      { text: 'Link', value: 'link' },
      { text: 'Trust level', value: 'trust_level' },
      { text: 'TLP', value: 'tlp_level', align: 'center' },
      { text: 'Source', value: 'source', align: 'center' },
      { text: 'In the Wild ?', value: 'is_in_the_wild', align: 'center' },
      { text: 'In the News ?', value: 'is_in_the_news', align: 'center' },
      { text: 'Last update', value: 'modified', align: 'center' },
      { text: 'Actions', value: 'action', sortable: false },
      { text: '', value: 'data-table-expand' },
    ],
    exploits: [],
    exploit_headers: [
      { text: 'Link', value: 'link' },
      { text: 'Trust level', value: 'trust_level' },
      { text: 'TLP', value: 'tlp_level', align: 'center' },
      { text: 'Source', value: 'source', align: 'center' },
      { text: 'Availability', value: 'availability', align: 'center' },
      { text: 'Maturity', value: 'maturity', align: 'center' },
      { text: 'Last update', value: 'modified', align: 'center' },
      { text: 'Actions', value: 'action', sortable: false },
      { text: '', value: 'data-table-expand' },
    ],
    editedIndex: -1,
    defaultMetadata: {
      link: 'https://',
      notes: '',
      trust_level: 'high',
      trust_level_items: ['unknown', 'low', 'medium', 'high'],
      tlp_level: 'white',
      tlp_level_items: ['white', 'green', 'amber', 'red', 'black'],
      source: 'manual',
      availability: 'public',
      availability_items: ['unknown', 'private', 'public'],
      maturity: 'unknown',
      maturity_items: ['unknown', 'unproven', 'poc', 'functional'],
      modified: '',
      is_in_the_wild: 0,
      is_in_the_news: 0,
      published: ''
    },
    editedItem: {},
    dialog_exploit: false,
    dialog_threat: false,
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  mounted() {
    this.vuln_id = this.$router.currentRoute.params.vuln_id;
    this.editedItem = this.defaultMetadata;
    this.getDataFromApi(this.vuln_id);
  },
  computed: {
    formExploitTitle() {
      return this.editedIndex === -1 ? 'New Exploit' : 'Edit Exploit'
    },
    formThreatTitle() {
      return this.editedIndex === -1 ? 'New threat activity' : 'Edit threat activity'
    },
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
      return this.ratings.score;
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
      // this.loading = true;
      return new Promise((resolve, reject) => {
        let vuln = this.getVulnDetails(vuln_id);
        let history = this.getHistory(vuln_id);
        let ratings = this.getRatings(vuln_id);
        let exploits = this.getExploits(vuln_id);
        let threats = this.getThreats(vuln_id);

        setTimeout(() => {
          this.loading = false;
          resolve({ vuln, history, ratings, exploits, threats });
        }, 300);
      });
    },
    getVulnDetails(vuln_id) {
      this.loading = true;
      this.$api.get('/api/vulns/'+vuln_id).then(res => {
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
    getRatings(vuln_id) {
      this.loading = true;
      this.$api.get('/api/ratings/calc/'+vuln_id).then(res => {
        this.ratings = res.data;
        return this.vuln;
      }).catch(e => {
        this.ratings = {};
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get vuln ratings',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading = false;
    },
    getExploits(vuln_id) {
      this.loading = true;
      this.$api.get('/api/vulns/'+vuln_id+'/exploits').then(res => {
        this.exploits = res.data;
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
      this.$api.get('/api/vulns/'+vuln_id+'/threats').then(res => {
        this.threats = res.data;
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
    getHistory(vuln_id) {
      this.loading = true;
      this.$api.get('/api/vulns/'+vuln_id+'/history').then(res => {
        this.history = res.data;
        return this.threats;
      }).catch(e => {
        this.history = {};
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get vuln history',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
      this.loading = false;
    },
    getCVSSColor(score) {
      if (score >= 9.0 ) return 'red darken-4';
      else if (score >= 7.0) return 'red';
      else if (score >= 4.0) return 'orange';
      else if (score >= 0.1) return 'yellow';
      else return 'grey';
    },
    getTLPColor(tlp_level) {
      if (tlp_level === 'white' ) return '';
      else if (tlp_level === 'green') return 'green';
      else if (tlp_level === 'amber') return 'orange';
      else if (tlp_level === 'red') return 'red';
      else if (tlp_level === 'black') return 'black';
      else return 'grey';
    },
    getRatingColor(rating) {
      if (rating >= 80 ) return 'red';
      else if (rating >= 60) return 'orange';
      else if (rating >= 40) return 'yellow';
      else if (rating >= 0) return 'blue';
      else return 'grey';
    },
    saveNewExploit() {
      // Save in backend
      this.editedItem.modified = new Date();
      this.$api.post('/api/vulns/'+this.vuln_id+'/exploits/add', this.editedItem).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Exploit successfuly saved.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to save the exploit metadata.';
        }

      }).catch(e => {
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to save related exploits',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
        this.dialog_exploit = false;
        this.editedItem = this.defaultMetadata;
        return;
      });

      // Update the datatable
      let new_exploit = JSON.parse(JSON.stringify(this.editedItem));
      if (this.editedIndex > -1) {
          Object.assign(this.exploits[this.editedIndex], new_exploit);
      } else {
          this.exploits.push(new_exploit);
      }

      // this.editedItem = this.defaultMetadata;
      this.editedItem = JSON.parse(JSON.stringify(this.defaultMetadata));
      this.dialog_exploit = false;
    },
    editExploit(item) {
      this.editedIndex = this.exploits.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog_exploit = true
      this.snack = true;
      this.snackColor = 'success';
      this.snackText = 'Exploit successfuly edited.';
    },
    deleteExploit(item) {
      // save in backend
      this.$api.get('/api/vulns/'+this.vuln_id+'/exploits/'+item.id+'/del').then(res => {
        if (res){
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Exploit successfuly deleted.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to delete the exploit';
        }
      }).catch(e => {
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to delete related exploit',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
        this.dialog_exploit = false;
        return;
      });

      this.editedIndex = this.exploits.indexOf(item);
      this.exploits.splice(this.editedIndex, 1)
    },
    saveNewThreat() {
      // Save in backend
      this.editedItem.modified = new Date();
      this.$api.post('/api/vulns/'+this.vuln_id+'/threats/add', this.editedItem).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Threat activity successfuly saved.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to save the threat activity.';
        }

      }).catch(e => {
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to save related threat activity',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
        this.dialog_threat = false;
        return;
      });

      // Update the datatable
      let new_threat = JSON.parse(JSON.stringify(this.editedItem));
      if (this.editedIndex > -1) {
          Object.assign(this.threats[this.editedIndex], new_threat);
      } else {
          this.threats.push(new_threat);
      }

      this.editedItem = JSON.parse(JSON.stringify(this.defaultMetadata));
      this.dialog_threat = false;
    },
    editThreat(item) {
      this.editedIndex = this.threats.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog_threat = true
      this.snack = true;
      this.snackColor = 'success';
      this.snackText = 'Threat activity successfuly edited.';
    },
    deleteThreat(item) {
      // save in backend
      this.$api.get('/api/vulns/'+this.vuln_id+'/threats/'+item.id+'/del').then(res => {
        if (res){
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Threat activity successfuly deleted.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to delete the threat activity';
        }
      }).catch(e => {
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to delete related threat activity',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
        this.dialog_threat = false;
        return;
      });

      this.editedIndex = this.threats.indexOf(item);
      this.threats.splice(this.editedIndex, 1)
    },
    viewRating() {
      this.$router.push({ 'name': 'Ratings', 'query': { 'vector': this.vuln_vector } });
    },
    toggleMonitored(item) {
      // save in backend
      let data = {
        'monitored': !this.vuln.monitored,
        'vuln_id': this.vuln.id,
        'organization_id': localStorage.getItem('org_id')
      };
      
      this.$api.put('/api/vulns/'+this.vuln_id+'/toggle', data).then(res => {
        if (res){
          this.vuln.monitored = !this.vuln.monitored;
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
}
</script>
