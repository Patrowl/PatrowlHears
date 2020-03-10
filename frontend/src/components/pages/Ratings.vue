<template>
    <v-container fluid grid-list-md>
      <v-layout row wrap>
        <v-flex md8 d-flex align-stretch>
          <v-card color="grey lighten-1" raised class="flex-grow-1">
            <v-card-title>Vector</v-card-title>
            <v-card-text>{{rating_vector}}</v-card-text>
          </v-card>
        </v-flex>
        <v-flex md3 align-stretch>
          <v-card :color="getRatingColor(parseInt(score))" raised>
            <v-card-title>Global Score</v-card-title>
            <v-card-text class="display-2 text-center">{{parseInt(score)}}</v-card-text>
          </v-card>
        </v-flex>
      </v-layout>

      <v-layout row wrap>
        <v-flex md8>
          <v-card color="grey lighten-5">
            <v-card-title>Vulnerability metrics</v-card-title>
            <v-card-text>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Access - Attack Vector &nbsp;</span>
                <v-btn-toggle
                  v-model="vulnerability.access.vector"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="L">Local (AV:L)</v-btn>
                  <v-btn small value="A">Adjacent Network (AV:A)</v-btn>
                  <v-btn small value="N">Network (AV:N)</v-btn>
                  <!-- <v-btn small value="P">Physical (AV:P)</v-btn> -->
                </v-btn-toggle>
              </v-col>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Access - Attack Complexity &nbsp;</span>
                <v-btn-toggle
                  v-model="vulnerability.access.complexity"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="H">High (AC:H)</v-btn>
                  <v-btn small value="M">Medium (AC:M)</v-btn>
                  <v-btn small value="L">Low (AC:L)</v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Access - Authentication &nbsp;</span>
                <v-btn-toggle
                  v-model="vulnerability.access.authentication"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="M">Multiple (Au:M)</v-btn>
                  <v-btn small value="S">Single (Au:S)</v-btn>
                  <v-btn small value="N">None (Au:N)</v-btn>
                </v-btn-toggle>
              </v-col>

              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Impact - Confidentiality &nbsp;</span>
                <v-btn-toggle
                  v-model="vulnerability.impact.confidentiality"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="N">None (C:N)</v-btn>
                  <v-btn small value="L">Low (C:L)</v-btn>
                  <v-btn small value="C">Complete (C:C)</v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Impact - Integrity &nbsp;</span>
                <v-btn-toggle
                  v-model="vulnerability.impact.integrity"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="N">None (I:N)</v-btn>
                  <v-btn small value="L">Low (I:L)</v-btn>
                  <v-btn small value="C">Complete (I:C)</v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Impact - Availability &nbsp;</span>
                <v-btn-toggle
                  v-model="vulnerability.impact.availability"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="N">None (A:N)</v-btn>
                  <v-btn small value="L">Low (A:L)</v-btn>
                  <v-btn small value="C">Complete (A:C)</v-btn>
                </v-btn-toggle>
              </v-col>

              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Remediation &nbsp;</span>
                <v-btn-toggle
                  v-model="vulnerability.remediation"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="X">Unknown (R:X)</v-btn>
                  <v-btn small value="U">Unavailable (R:H)</v-btn>
                  <v-btn small value="W">Workaround (R:W)</v-btn>
                  <v-btn small value="T">Temporary (R:T)</v-btn>
                  <v-btn small value="O">Official (R:O)</v-btn>
                </v-btn-toggle>
              </v-col>
              <!-- <v-col cols="4" class="py-2">
                <v-switch
                  v-model="vulnerability.confirmation"
                  :label="`Confirmed ? : ${vulnerability.confirmation.toString()}`"
                  color="deep-orange"
                  ></v-switch>
              </v-col> -->

              <v-row>
                <v-col cols="4" class="py-2 pa-6">
                  <span class="subtitle-1">Vulnerability Age &nbsp;</span>
                  <v-menu
                    ref="menu_vage"
                    v-model="menu_vage"
                    :close-on-content-click="false"
                    :return-value.sync="vulnerability.age"
                    transition="scale-transition"
                    offset-y
                    min-width="290px"
                  >
                    <template v-slot:activator="{ on }">
                      <v-text-field
                        v-model="vulnerability.age"
                        v-on="on"
                      ></v-text-field>
                    </template>
                    <v-date-picker v-model="vulnerability.age" scrollable landscape>
                      <v-spacer></v-spacer>
                      <v-btn text color="primary" @click="menu_vage = false">Cancel</v-btn>
                      <v-btn text color="primary" @click="$refs.menu_vage.save('')">Reset</v-btn>
                      <v-btn text color="primary" @click="$refs.menu_vage.save(vulnerability.age)">OK</v-btn>
                    </v-date-picker>
                  </v-menu>
                </v-col>
                <v-col cols="8" class="py-2">
                  <span class="subtitle-1">Confirmation &nbsp;</span>
                  <v-row>
                    <v-col cols="12" class="py-2">
                      <v-switch
                        v-model="vulnerability.confirmation"
                        :label="`Confirmed by trusted parties: ${vulnerability.confirmation.toString()}`"
                        color="deep-orange"
                        ></v-switch>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex md3 d-flex align-stretch>
          <v-card color="grey lighten-5" class="flex-grow-1 flex-shrink-0">
            <v-card-title>Vulnerability Score</v-card-title>
            <v-card-text class="text-center">
              <v-progress-circular
                :value="vuln_score*20"
                :size="100"
                :width="5"
                color="deep-orange"
              >{{parseInt(vuln_score*20)}}
              </v-progress-circular>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>

      <v-layout row wrap>
        <v-flex md8>
          <v-card color="grey lighten-5">
            <v-card-title>Threat metrics</v-card-title>
            <v-card-text>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Exploit Availability &nbsp;</span>
                <v-btn-toggle
                  v-model="threat.exploit_availability"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="X">Unknown (EA:X)</v-btn>
                  <v-btn small value="R">Private (EA:R)</v-btn>
                  <v-btn small value="U">Public (EA:U)</v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Exploit Maturity &nbsp;</span>
                <v-btn-toggle
                  v-model="threat.exploit_maturity"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="X">Unknown (EM:X)</v-btn>
                  <v-btn small value="U">Unproven (EM:U)</v-btn>
                  <v-btn small value="P">PoC (EM:P)</v-btn>
                  <v-btn small value="F">Functional (EM:F)</v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Exploit Confidence &nbsp;</span>
                <v-btn-toggle
                  v-model="threat.exploit_trust"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="X">Unknown (ET:X)</v-btn>
                  <v-btn small value="L">Low (ET:L)</v-btn>
                  <v-btn small value="M">Medium (ET:M)</v-btn>
                  <v-btn small value="H">High (ET:H)</v-btn>
                </v-btn-toggle>
              </v-col>
              <v-row>
                <v-col cols="4" class="py-2 pa-6">
                  <span class="subtitle-1">Exploit Age &nbsp;</span>
                  <v-menu
                    ref="menu"
                    v-model="menu"
                    :close-on-content-click="false"
                    :return-value.sync="threat.exploit_age"
                    transition="scale-transition"
                    offset-y
                    min-width="290px"
                  >
                    <template v-slot:activator="{ on }">
                      <v-text-field
                        v-model="threat.exploit_age"
                        v-on="on"
                      ></v-text-field>
                    </template>
                    <v-date-picker v-model="threat.exploit_age" scrollable landscape>
                      <v-spacer></v-spacer>
                      <v-btn text color="primary" @click="menu == false">Cancel</v-btn>
                      <v-btn text color="primary" @click="$refs.menu.save('')">Reset</v-btn>
                      <v-btn text color="primary" @click="$refs.menu.save(threat.exploit_age)">OK</v-btn>
                    </v-date-picker>
                  </v-menu>
                </v-col>
                <v-col cols="8" class="py-2">
                  <span class="subtitle-1">Mediatisation &nbsp;</span>
                  <v-row>
                    <v-col cols="6" class="py-2">
                      <v-switch
                        v-model="threat.in_the_news"
                        :label="`In the News ? : ${threat.in_the_news.toString()}`"
                        color="deep-orange"
                        ></v-switch>
                    </v-col>
                    <v-col cols="6" class="py-2">
                      <v-switch
                        v-model="threat.in_the_wild"
                        :label="`In the Wild ? : ${threat.in_the_wild.toString()}`"
                        color="deep-orange"
                        ></v-switch>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex md3 d-flex align-stretch>
          <v-card color="grey lighten-5" class="flex-grow-1 flex-shrink-0">
            <v-card-title>Threat Score</v-card-title>
            <v-card-text class="text-center">
              <v-progress-circular
                :value="threat_score*20"
                :size="100"
                :width="5"
                color="deep-orange"
              >{{parseInt(threat_score*20)}}
              </v-progress-circular>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>

      <v-layout row wrap>
        <v-flex md8>
          <v-card color="grey lighten-5">
            <v-card-title>Asset metrics</v-card-title>
            <v-card-text>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Criticality &nbsp;</span>
                <v-btn-toggle
                  v-model="asset.criticality"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="X">Unknown (Cr:X)</v-btn>
                  <v-btn small value="L">Low (Cr:L)</v-btn>
                  <v-btn small value="M">Medium (Cr:M)</v-btn>
                  <v-btn small value="H">High (Cr:H)</v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Exposure &nbsp;</span>
                <v-btn-toggle
                  v-model="asset.exposure"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="X">Unknown (E:X)</v-btn>
                  <v-btn small value="R">Restricted/DMZ (E:R)</v-btn>
                  <v-btn small value="I">Internal (E:I)</v-btn>
                  <v-btn small value="E">External (E:E)</v-btn>
                </v-btn-toggle>
              </v-col>
              <v-col cols="4" class="py-2">
                <span class="subtitle-1">Distribution &nbsp;</span>
                <v-btn-toggle
                  v-model="asset.distribution"
                  color="deep-orange accent-3"
                  mandatory
                >
                  <v-btn small value="X">Unknown (D:X)</v-btn>
                  <v-btn small value="L">Low <15 (D:L)</v-btn>
                  <v-btn small value="M">Medium <45 (D:M)</v-btn>
                  <v-btn small value="H">High &ge;45 (D:H)</v-btn>
                </v-btn-toggle>
              </v-col>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex md3 d-flex align-stretch>
          <v-card color="grey lighten-5" class="flex-grow-1 flex-shrink-0">
            <v-card-title>Asset Score</v-card-title>
            <v-card-text class="text-center">
              <v-progress-circular
                :value="asset_score*25"
                :size="100"
                :width="5"
                color="deep-orange"
              >{{parseInt(asset_score*25)}}
              </v-progress-circular>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
</template>

<script>
import Colors from "../../common/colors";
import Scores from "../../common/scores";
import moment from 'moment';
export default {
  name: "Ratings",
  mixins: [Colors, Scores],
  data: () => ({
    loading: false,
    vulnerability: {
      // cvss2_base_score: 'X',
      access: {
        vector: 'N',
        complexity: 'L',
        authentication: 'N'
      },
      impact: {
        confidentiality: 'N',
        integrity: 'N',
        availability: 'N'
      },
      confirmation: true,
      remediation: 'X',
      age: new Date().toISOString().substr(0, 10)
    },
    threat: {
      exploit_availability: 'X',
      exploit_maturity: 'X',
      exploit_trust: 'X',
      exploit_age: new Date().toISOString().substr(0, 10),
      in_the_news: false,
      in_the_wild: false
    },
    asset: {
      criticality: 'M',
      exposure: 'I',
      distribution: 'M'
    },
    metrics_values: {},
    base_vector: '',
    base_vector_format: 'VPRv1',
    score: 'n/a',
    vuln_score: 80,
    threat_score: 0,
    asset_score: 0,
    menu: false,
    menu_vage: false,
  }),
  mounted() {
    this.base_vector = this.$route.query.vector;
    this.getDataFromApi();
    if (this.base_vector != null || this.base_vector != '') {
      this.init_vector(this.base_vector);
    };
  },
  computed: {
    rating_vector() {
      let vector = [];
      // Vulnerability metrics
      let vuln_subvector = [];
      vuln_subvector.push('AV:'+this.vulnerability.access.vector);
      vuln_subvector.push('AC:'+this.vulnerability.access.complexity);
      vuln_subvector.push('Au:'+this.vulnerability.access.authentication);
      vuln_subvector.push('C:'+this.vulnerability.impact.confidentiality);
      vuln_subvector.push('I:'+this.vulnerability.impact.integrity);
      vuln_subvector.push('A:'+this.vulnerability.impact.availability);
      this.vulnerability.confirmation == true ? vuln_subvector.push('CL:Y'):null;
      this.vulnerability.remediation != 'X' ? vuln_subvector.push('R:'+this.vulnerability.remediation):null;
      if (this.vulnerability.age != '') {
        vuln_subvector.push('VX:'+moment().diff(this.vulnerability.age, 'days'));
      }
      this.vuln_score = this.calcVulnScore(vuln_subvector, this.metrics_values.vulnerability);
      vector = vector.concat(vuln_subvector);

      // Threat metrics
      let threat_subvector = [];
      this.threat.exploit_availability != 'X' ? threat_subvector.push('EA:'+this.threat.exploit_availability):null;
      this.threat.exploit_maturity != 'X' ? threat_subvector.push('EM:'+this.threat.exploit_maturity):null;
      this.threat.exploit_trust != 'X' ? threat_subvector.push('ET:'+this.threat.exploit_trust):null;
      this.threat.in_the_news === true ? threat_subvector.push('N:Y'):null;
      this.threat.in_the_wild === true ? threat_subvector.push('W:Y'):null;
      if (this.threat.exploit_age != '') {
        threat_subvector.push('EX:'+moment().diff(this.threat.exploit_age, 'days'));
      }
      this.threat_score = this.calcThreatScore(threat_subvector, this.metrics_values.threat);
      vector = vector.concat(threat_subvector);

      // Asset metrics
      let asset_subvector = [];
      this.asset.criticality != 'X' ? asset_subvector.push('Cr:'+this.asset.criticality):null;
      this.asset.exposure != 'X' ? asset_subvector.push('E:'+this.asset.exposure):null;
      this.asset.distribution != 'X' ? asset_subvector.push('D:'+this.asset.distribution):null;
      this.asset_score = this.calcAssetScore(asset_subvector, this.metrics_values.asset);
      vector = vector.concat(asset_subvector);

      this.score = (this.vuln_score * 12) + (this.threat_score * 4) + (this.asset_score * 5)
      return vector.join('/');
    },
  },
  methods: {
    init_vector(vector) {
      if (vector == undefined || Object.keys(vector).length === 0) return 0;
      let m = "";
      let metrics = vector.split('/');
      for(let i = 0; i < metrics.length; i++) {
        m = metrics[i].split(':');
        // Vulnerability
        m[0] == 'AV' ? this.vulnerability.access.vector = m[1]:null;
        m[0] == 'AC' ? this.vulnerability.access.complexity = m[1]:null;
        m[0] == 'Au' ? this.vulnerability.access.authentication = m[1]:null;
        m[0] == 'C' ? this.vulnerability.impact.confidentiality = m[1]:null;
        this.vulnerability.impact.confidentiality == 'P' ? this.vulnerability.impact.confidentiality = 'L':null;
        m[0] == 'I' ? this.vulnerability.impact.integrity = m[1]:null;
        this.vulnerability.impact.integrity == 'P' ? this.vulnerability.impact.integrity = 'L':null;
        m[0] == 'A' ? this.vulnerability.impact.availability = m[1]:null;
        this.vulnerability.impact.availability == 'P' ? this.vulnerability.impact.availability = 'L':null;
        metrics[i] == 'CL:Y' ? this.vulnerability.confirmation = true:null;
        m[0] == 'R' ? this.vulnerability.remediation = m[1]:null;
        m[0] == 'VX' ? this.vulnerability.age = moment().subtract(m[1], "days").toISOString(true).substr(0, 10):'';

        // Threat
        m[0] == 'EA' ? this.threat.exploit_availability = m[1]:null;
        m[0] == 'EM' ? this.threat.exploit_maturity = m[1]:null;
        m[0] == 'ET' ? this.threat.exploit_trust = m[1]:null;
        metrics[i] == 'N:Y' ? this.threat.in_the_news = true:null;
        metrics[i] == 'W:Y' ? this.threat.in_the_wild = true:null;
        m[0] == 'VX' ? this.threat.exploit_age = moment().subtract(m[1], "days").toISOString(true).substr(0, 10):'';

        // Assets
        m[0] == 'Cr' ? this.asset.criticality = m[1]:null;
        m[0] == 'E' ? this.asset.exposure = m[1]:null;
        m[0] == 'D' ? this.asset.distribution = m[1]:null;
      }
    },
    getDataFromApi() {
      this.loading = true;
      return new Promise((resolve, reject) => {
        let metrics_values = this.getMetricValues();

        setTimeout(() => {
          resolve({
            metrics_values
          });
        }, 300);
      });
      this.loading = false;
    },
    getMetricValues() {
      this.$api.get('/api/ratings/metrics').then(res => {
        this.metrics_values = res.data;
        this.loading = false;
        return this.metrics_values;
      }).catch(e => {
        this.metrics_values = {};
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get metrics values',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
    },
  },

};
</script>
