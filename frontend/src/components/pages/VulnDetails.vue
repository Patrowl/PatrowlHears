<template>
  <v-tabs
    left
    background-color="white"
    color="deep-orange accent-4"
  >
    <v-tab>Summary</v-tab>
    <v-tab>
      <v-badge color="deep-orange" :content="this.exploits.length">Exploits</v-badge>
    </v-tab>
    <v-tab>
      <v-badge color="deep-orange" :content="this.threats.length">Activities</v-badge>
    </v-tab>
    <!-- <v-tab>Metadata</v-tab> -->
    <!-- <v-tab>Assets</v-tab> -->
    <v-tab>Timeline</v-tab>

    <!-- Summary -->
    <v-tab-item>
      <v-container fluid grid-list-md>
        <v-layout row wrap>

          <v-flex md8>
            <!-- Summary -->
            <v-card color="grey lighten-5">
              <v-card-title primary class="title">Vuln ID: PH-{{ $route.params.vuln_id }}</v-card-title>
              <v-card-text>
                <v-list
                  subheader
                  color="grey lighten-5"
                >
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>CVE</v-list-item-subtitle>
                      {{this.vuln.cve}}
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
                  <!-- </v-list> -->

                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-subtitle>Summary</v-list-item-subtitle>
                      {{this.vuln.summary}}
                    </v-list-item-content>
                  </v-list-item>
                <!-- </v-list> -->

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
              <v-card color="red lighten-1">
                <v-card-title primary class="title">Graph here</v-card-title>
                <v-card-text>la, la, la et la</v-card-text>
              </v-card>
            </v-flex>
            <v-flex>
              <v-card color="grey lighten-5">
                <v-card-title primary class="title">Metrics</v-card-title>
                <v-card-text>
                  Exploitable ?: {{this.vuln.is_exploitable}}<br/>
                  Confirmed ?: {{this.vuln.is_confirmed}}<br/>
                  In the news ?: {{this.vuln.is_in_the_news}}<br/>
                  Exploited in the wild ?: {{this.vuln.is_in_the_wild}}
                </v-card-text>
              </v-card>
            </v-flex>
            <!-- <v-flex>
              <v-card color="grey lighten-5">
                <v-card-title primary class="title">Impact</v-card-title>
                <v-card-text>
                  Confidentiality: {{this.vuln.impact.confidentiality}}<br/>
                  Integrity: {{this.vuln.impact.integrity}}<br/>
                  Availability: {{this.vuln.impact.availability}}<br/>
                </v-card-text>
              </v-card>
            </v-flex>
            <v-flex>
              <v-card color="grey lighten-5">
                <v-card-title primary class="title">Access</v-card-title>
                <v-card-text>
                  Authentication: {{this.vuln.access.authentication}}<br/>
                  Complexity: {{this.vuln.access.complexity}}<br/>
                  Vector: {{this.vuln.access.vector}}<br/>
                </v-card-text>
              </v-card>
            </v-flex> -->

            <v-flex>
              <v-row no-gutters>
                <v-col cols="12" sm="6">
                  <v-card color="grey lighten-5">
                    <v-card-title primary class="title">Impact</v-card-title>
                    <v-card-text>
                      Confidentiality: {{this.vuln.impact.confidentiality}}<br/>
                      Integrity: {{this.vuln.impact.integrity}}<br/>
                      Availability: {{this.vuln.impact.availability}}<br/>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-card color="grey lighten-5" >
                    <v-card-title primary class="title">Access</v-card-title>
                    <v-card-text>
                      Authentication: {{this.vuln.access.authentication}}<br/>
                      Complexity: {{this.vuln.access.complexity}}<br/>
                      Vector: {{this.vuln.access.vector}}<br/>
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
      <v-card>
        <v-data-table
          :headers="exploit_headers"
          :items="exploits"
          class="elevation-4"
          item-key="id"
          multi-sort
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
                  <v-select v-model="editedItem.tlp_level" label="TLP Level" :items="editedItem.tlp_level_items"></v-select>
                  <v-text-field v-model="editedItem.source" label="Source"></v-text-field>
                  <v-select v-model="editedItem.availability" label="Availability" :items="editedItem.availability_items"></v-select>
                  <v-select v-model="editedItem.maturity" label="Maturity" :items="editedItem.maturity_items"></v-select>
                  <v-btn color="success" @click="saveNewExploit">
                    Save
                  </v-btn>
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
                <v-form ref="form-new-exploit">
                  <v-text-field v-model="editedItem.link" label="link"></v-text-field>
                  <v-select v-model="editedItem.tlp_level" label="TLP Level" :items="editedItem.tlp_level_items"></v-select>
                  <v-text-field v-model="editedItem.source" label="Source"></v-text-field>
                  <v-select v-model="editedItem.availability" label="Availability" :items="editedItem.availability_items"></v-select>
                  <v-select v-model="editedItem.maturity" label="Maturity" :items="editedItem.maturity_items"></v-select>
                  <v-btn color="success" @click="saveNewThreat">
                    Save
                  </v-btn>
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

  </v-tabs>



</template>

<script>
import axios from 'axios';
import swal from 'sweetalert2';
import router from '../../router';

export default {
  name: 'VulnDetails',
  data: () => ({
    vuln_id: "",
    vuln: {
      cwe_id: '',
      impact: {confidentiality: '', integrity: '', availability: ''},
      access: {authentication: '', complexity: '', vector: ''},
    },
    threats: {},
    threat_headers: [
      // { text: 'ID', value: 'publicid' },
      { text: 'Link', value: 'link' },
      { text: 'Trust level', value: 'trust_level' },
      { text: 'TLP', value: 'tlp_level', align: 'center' },
      { text: 'Source', value: 'source', align: 'center' },
      { text: 'In the Wild ?', value: 'is_in_the_wild', align: 'center' },
      { text: 'In the News ?', value: 'is_in_the_news', align: 'center' },
      { text: 'Last update', value: 'modified', align: 'center' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    exploits: [],
    exploit_headers: [
      // { text: 'ID', value: 'publicid' },
      { text: 'Link', value: 'link' },
      { text: 'Trust level', value: 'trust_level' },
      { text: 'TLP', value: 'tlp_level', align: 'center' },
      { text: 'Source', value: 'source', align: 'center' },
      { text: 'Availability', value: 'availability', align: 'center' },
      { text: 'Maturity', value: 'maturity', align: 'center' },
      { text: 'Last update', value: 'modified', align: 'center' },
      { text: 'Actions', value: 'action', sortable: false },
    ],
    editedIndex: -1,
    editedItem: {
      link: 'https://',
      trust_level: 'trusted',
      trust_level_items: ['unknown', 'low', 'medium', 'trusted'],
      tlp_level: 'white',
      tlp_level_items: ['white', 'green', 'amber', 'red', 'black'],
      source: 'manual',
      availability: 'unknown',
      availability_items: ['unknown', 'private', 'public'],
      maturity: 'unknown',
      maturity_items: ['unknown', 'unproven', 'poc', 'functional'],
      modified: '',
      is_in_the_wild: 1,
      is_in_the_news: 1,
      published: ''
    },
    dialog_exploit: false,
    dialog_threat: false,
    snack: false,
    snackColor: '',
    snackText: '',
    // assets: {},
  }),
  mounted() {
    this.vuln_id = this.$router.currentRoute.params.vuln_id;
    this.getDataFromApi(this.vuln_id);
  },
  computed: {
    formExploitTitle () {
      return this.editedIndex === -1 ? 'New Exploit' : 'Edit Exploit'
    },
    formThreatTitle () {
      return this.editedIndex === -1 ? 'New threat activity' : 'Edit threat activity'
    },
  },
  methods: {
    getDataFromApi(vuln_id) {
      // this.loading = true;
      return new Promise((resolve, reject) => {
        let vuln = this.getdetails(vuln_id);
        let exploits = this.getExploits(vuln_id);
        let threats = this.getThreats(vuln_id);

        setTimeout(() => {
          this.loading = false;
          resolve({
            vuln, exploits, threats
          });
        }, 300);
      });
    },
    getdetails(vuln_id) {
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
    saveNewExploit() {
      // Save in backend
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
        return;
      });

      // Update the datatable
      if (this.editedIndex > -1) {
          Object.assign(this.exploits[this.editedIndex], this.editedItem);
      } else {
          this.exploits.push(this.editedItem);
      }
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
      if (this.editedIndex > -1) {
          Object.assign(this.exploits[this.editedIndex], this.editedItem);
      } else {
          this.threats.push(this.editedItem);
      }
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
    deleteThreatt(item) {
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
  }
}
</script>
