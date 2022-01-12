<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ formVulnTitle }}</span>
    </v-card-title>
    <v-card-text>
      <v-form ref="form-vuln">
        <v-container>
          <v-row>
            <v-col md="6">
              <v-text-field v-model="editedItem.cve_id" label="CVE ID"></v-text-field>
            </v-col>
            <v-col md="3">
              <v-select
                v-model="editedItem.monitored"
                label="Is monitored?"
                :items="editedItem.monitored_items"
                ></v-select>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-textarea
                v-model="editedItem.summary"
                label="Summary"
                hint="Insert notes about this vulnerability"
                rows="4"
                ></v-textarea>
            </v-col>
          </v-row>
          <v-row>
            <v-col md="3">
              <v-text-field v-model="editedItem.cvss2" label="CVSSv2 Score"></v-text-field>
            </v-col>
            <v-col md="9">
              <v-text-field v-model="editedItem.cvss2_vector" label="CVSSv2 Vector"></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col md="3">
              <v-text-field v-model="editedItem.cvss3" label="CVSSv3 Score"></v-text-field>
            </v-col>
            <v-col md="9">
              <v-text-field v-model="editedItem.cvss3_vector" label="CVSSv3 Vector"></v-text-field>
            </v-col>
          </v-row>
          Impact
          <v-row>
            <v-col cols="12" md="4">
              <v-select
                v-model="editedItem.impact_confidentiality"
                label="Confidentiality"
                :items="editedItem.impact_confidentiality_items"></v-select>
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="editedItem.impact_integrity"
                label="Integrity"
                :items="editedItem.impact_integrity_items"></v-select>
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="editedItem.impact_availability"
                label="Availability"
                :items="editedItem.impact_availability_items"></v-select>
            </v-col>
          </v-row>
          Access
          <v-row>
            <v-col cols="12" md="4">
              <v-select
                v-model="editedItem.access_authentication"
                label="Authentication"
                :items="editedItem.access_authentication_items"></v-select>
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="editedItem.access_complexity"
                label="Complexity"
                :items="editedItem.access_complexity_items"></v-select>
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="editedItem.access_vector"
                label="Vector"
                :items="editedItem.access_vector_items"></v-select>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="3">
              <v-select
                v-model="editedItem.is_exploitable"
                label="Is exploitable?"
                :items="editedItem.is_exploitable_items"
                ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="editedItem.is_confirmed"
                label="Is confirmed?"
                :items="editedItem.is_confirmed_items"
                ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="editedItem.is_in_the_news"
                label="In the News?"
                :items="editedItem.is_in_the_news_items"
                ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="editedItem.is_in_the_wild"
                label="In The Wild"
                :items="editedItem.is_in_the_wild_items"></v-select>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-autocomplete
                v-model="editedItem.products"
                :items="products_items"
                :loading="products_isLoading"
                :search-input.sync="products_search"
                chips
                cache-items
                hide-details
                hide-selected
                hide-no-data
                item-text="name"
                item-value="id"
                label="Search for a product..."
                multiple
              >
                <template v-slot:selection="data">
                  <v-chip
                    v-bind="data.attrs"
                    :input-value="data.selected"
                    close
                    @click="data.select"
                    @click:close="removeSelectedProduct(data.item)"
                  >
                    {{ data.item.vendor }}/{{ data.item.name }}
                  </v-chip>
                </template>
                <template v-slot:item="data">
                  {{ data.item.vendor }}/{{ data.item.name }}
                </template>
              </v-autocomplete>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-textarea
                v-model="editedItem.cpes"
                label="CPE list"
                hint="Insert CPEs (line by line or comma-separated)"
                rows="3"
                ></v-textarea>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-textarea
                v-model="editedItem.references"
                label="References links"
                hint="Insert links (line by line or comma-separated)"
                rows="3"
                ></v-textarea>
            </v-col>
          </v-row>
          <v-btn color="success" @click="saveVuln">Save</v-btn>
          <v-btn color="warning" type="reset">Reset</v-btn>
        </v-container>
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer></v-spacer>
    </v-card-actions>

    <v-snackbar v-model="snack" :timeout="3000" :color="snackColor" dense>
      {{ snackText }}
      <v-btn text @click="snack = false">Close</v-btn>
    </v-snackbar>
  </v-card>
</template>

<script>
import _ from 'lodash';

export default {
  name: "VulnAddEdit",
  props: ['vuln', 'action'],
  data: () => ({
    editedIndex: -1,
    editedItem: {},
    defaultVulnMetadata: {
      id: '',
      cve_id: '',
      summary: '',
      published: '',
      cvss2: '',
      cvss2_vector: '',
      cvss3: '',
      cvss3_vector: '',
      cwe: '',
      access_authentication: 'NONE',
      access_authentication_items: ['NONE', 'SINGLE', 'MULTIPLE'],
      access_complexity: 'LOW',
      access_complexity_items: ['LOW', 'MEDIUM', 'HIGH'],
      access_vector: 'LOCAL',
      access_vector_items: ['LOCAL', 'ADJACENT_NETWORK', 'NETWORK'],
      impact_availability: 'NONE',
      impact_availability_items: ['NONE', 'PARTIAL', 'COMPLETE'],
      impact_confidentiality: 'NONE',
      impact_confidentiality_items: ['NONE', 'PARTIAL', 'COMPLETE'],
      impact_integrity: 'NONE',
      impact_integrity_items: ['NONE', 'PARTIAL', 'COMPLETE'],
      references: [],
      cpes: '',
      products: [],
      references: [],
      monitored: false,
      monitored_items: [
        { text: 'Yes', value: true},
        { text: 'No', value: false},
      ],
      is_exploitable: false,
      is_exploitable_items: [
        { text: 'Yes', value: true},
        { text: 'No', value: false},
      ],
      is_confirmed: false,
      is_confirmed_items: [
        { text: 'Yes', value: true},
        { text: 'No', value: false},
      ],
      is_in_the_wild: false,
      is_in_the_wild_items: [
        { text: 'Yes', value: true},
        { text: 'No', value: false},
      ],
      is_in_the_news: false,
      is_in_the_news_items: [
        { text: 'Yes', value: true},
        { text: 'No', value: false},
      ],
    },
    products_isLoading: false,
    products_autocomplete: null,
    products_items: [],
    products_search: null,
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  mounted() {
    if (this.action == 'edit') {
      this.loadVuln()
    } else {
      this.editedItem = this.defaultVulnMetadata;
    }
  },
  watch: {
    products_search: _.debounce(function (val) {

      if (val == null) return

      // Min 3 chars
      if (val.length < 3) return

      // Items have already been requested
      if (this.products_isLoading) return

      this.products_isLoading = true

      this.$api.get('/api/kb/products/?limit=30&search='+this.products_search)
        .then(res => {
          this.products_items = res.data.results;
        })
        .catch(err => {
          console.log(err);
        })
        .finally(() => (this.products_isLoading = false))
    }, 500),
  },
  computed: {
    formVulnTitle() {
      return this.editedIndex === -1 ? 'New Vulnerability' : 'Edit Vulnerability PH-'+this.vuln.id
    },
  },
  methods: {
    loadVuln() {
      this.editedIndex = 0;
      this.editedItem = this.defaultVulnMetadata;
      this.editedItem.cve_id = this.vuln.cveid;
      this.editedItem.summary = this.vuln.summary;
      this.editedItem.monitored = this.vuln.monitored;
      this.editedItem.cvss2 = this.vuln.cvss;
      this.editedItem.cvss2_vector = this.vuln.cvss_vector;
      this.editedItem.access_authentication = this.vuln.access.authentication;
      this.editedItem.access_complexity = this.vuln.access.complexity;
      this.editedItem.access_vector = this.vuln.access.vector;
      this.editedItem.impact_availability = this.vuln.impact.availability;
      this.editedItem.impact_confidentiality = this.vuln.impact.confidentiality;
      this.editedItem.impact_integrity = this.vuln.impact.integrity;
      this.editedItem.is_exploitable = this.vuln.is_exploitable;
      this.editedItem.is_confirmed = this.vuln.is_confirmed;
      this.editedItem.is_in_the_wild = this.vuln.is_in_the_wild;
      this.editedItem.is_in_the_news = this.vuln.is_in_the_news;
      this.editedItem.cpes = String(this.vuln.vulnerable_products).split(",").join("\n");
      this.editedItem.references = String(this.vuln.reflinks).split(",").join("\n");
      this.products_items = this.vuln.products;
      this.editedItem.products = this.vuln.products;
    },
    saveVuln() {
      // Save in backend
      this.editedItem.modified = new Date();

      if (this.editedIndex === -1) {
        // New vulnerability
        this.$api.post('/api/vulns/add', this.editedItem).then(res => {
          if (res && res.status === 200 && res.data.status == "success") {
            this.snack = true;
            this.snackColor = 'success';
            this.snackText = 'Vulnerability successfuly saved.';
          } else {
            if ('status' in res.data && 'reason' in res.data){
              this.snackText = 'Unable to save the vulnerability: '+res.data.reason;
            } else {
              this.snackText = 'Unable to save the vulnerability.';
            }
            this.snack = true;
            this.snackColor = 'error';
          }
        }).catch(e => {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to save the vulnerability.';
        });
      } else {
        // Edit vulnerability
        this.$api.post('/api/vulns/edit', this.editedItem).then(res => {
          if (res && res.status === 200) {
            this.snack = true;
            this.snackColor = 'success';
            // this.snackText = 'Vulnerability successfuly updated.';
            this.snackText = 'Not implemented.';
          } else {
            if ('status' in res.data && 'reason' in res.data){
              this.snackText = 'Unable to update the vulnerability: '+res.data.reason;
            } else {
              this.snackText = 'Unable to update the vulnerability.';
            }
            this.snack = true;
            this.snackColor = 'error';
            this.snackText = 'Unable to update the vulnerability.';
          }

        }).catch(e => {
          this.dialog_vuln = false;
          this.editedItem = this.defaultVulnMetadata;
        });
      }

      this.dialog_vuln = false;
      this.editedItem = this.defaultVulnMetadata;

      // Wait and reload page
      setTimeout(() => {
        this.$router.go();
      }, 2000);

    },
    removeSelectedProduct(item) {
      let index = -1
      if(this.editedIndex === -1){
        // Add new vulnerability
        index = this.editedItem.products.indexOf(item.id);
      } else {
        // Edit
        index = this.editedItem.products.findIndex(p => p.id == item.id);
      }
      if (index >= 0) this.editedItem.products.splice(index, 1);

    },
  }
};
</script>

<style>
.v-dialog {
    position: absolute;
    left: 0;
}
</style>
