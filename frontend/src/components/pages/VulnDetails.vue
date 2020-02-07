<template>
  <v-tabs
    left
    background-color="white"
    color="deep-orange accent-4"
  >
    <v-tab>Summary</v-tab>
    <v-tab>
      <v-badge color="deep-orange" :content="this.exploits.length" >Exploits</v-badge>
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
                    v-if="this.vuln.cwe_id != None"
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

          <!-- <v-flex d-flex xs12 sm6 md2 child-flex>
            <v-card color="green lighten-2" dark>
              <v-card-title primary class="title">Lorem</v-card-title>
              <v-card-text>{{lorem.slice(0,90)}}</v-card-text>
            </v-card>
          </v-flex> -->
          <!-- <v-flex d-flex xs12 sm6 md3>
            <v-card color="blue lighten-2" dark>
              <v-card-title primary class="title">Lorem</v-card-title>
              <v-card-text>{{lorem.slice(0,100)}}</v-card-text>
            </v-card>
          </v-flex> -->
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
          <a :href="item.link" class="drag" :transfer-data="{ 'example': 'drag-html' }">{{item.link}}</a>
        </template>

        <!-- Updated at -->
        <template v-slot:item.modified="{ item }">
          <span>{{moment(item.modified).format('YYYY-MM-DD')}}</span>
        </template>

        <!-- Actions -->
        <template v-slot:item.action="{ item }">
          <v-icon small class="mdi mdi-pencil" color="orange" @click="editExploit(item)"></v-icon>
          <v-icon small class="mdi mdi-delete" color="red" @click="deleteExploit(item)"></v-icon>
        </template>

        </v-data-table>
      </v-card>
    </v-tab-item>
  </v-tabs>

</template>

<script>
import axios from 'axios';
import swal from 'sweetalert2';
import router from '../../router';
// import { Drag, Drop } from 'vue-drag-drop';

export default {
  name: 'VulnDetails',
  // components: { Drag, Drop },
  data: () => ({
    lorem: `Lorem ipsum dolor sit amet, mel at clita quando. Te sit oratio
     vituperatoribus, nam ad ipsum posidonium mediocritatem, explicari dissentiunt cu mea.
      Repudiare disputationi vim in, mollis iriure nec cu, alienum argumentum ius ad. Pri eu
      justo aeque torquatos.`,
    vuln_id: "",
    vuln: {},
    exploits: {},
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
    assets: {},
  }),
  mounted() {
    this.vuln_id = this.$router.currentRoute.params.vuln_id;
    this.getDataFromApi(this.vuln_id);
  },
  methods: {
    getDataFromApi(vuln_id) {
      // this.loading = true;
      return new Promise((resolve, reject) => {
        let vuln = this.getdetails(vuln_id);
        let exploits = this.getexploits(vuln_id);

        setTimeout(() => {
          this.loading = false;
          resolve({
            vuln, exploits
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
        })
      });
      this.loading = false;
    },
    getexploits(vuln_id) {
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
        })
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
    handleDrop(data, event) {
      console.log(data);
      console.log(event);
      alert(`You dropped with data: ${JSON.stringify(data)}`);
    }
  }
}
</script>
