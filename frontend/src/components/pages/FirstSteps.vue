<template>
  <div>
    <v-stepper non-linear light v-model="stepper_fs">
      <v-stepper-header>
        <v-stepper-step editable step="1" color="deep-orange">Welcome</v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step editable step="2" color="deep-orange">Monitoring</v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step editable step="3" color="deep-orange">Alerting</v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step editable step="4" color="deep-orange">Finish</v-stepper-step>
      </v-stepper-header>

      <v-stepper-content step="1">
        <v-card
          class="mb-6"
          height="200px"
          tile
        >
          <v-card-title>
            Welcome in CanPatch !
          </v-card-title>
          <v-card-text>
            <strong>CanPatch</strong> is an advanced platform offering a continuous watch on vulnerabilities found on your IT assets, enriched by cyber-threat Intelligence data.<br/><br/>
            Let's get started. Click 'Next' button to continue.
          </v-card-text>
        </v-card>
        <v-btn color="grey" @click="nextStep(1)">Next<v-icon>mdi-chevron-right</v-icon></v-btn>
      </v-stepper-content>
      <v-stepper-content step="2">
        <v-card
          class="mb-6"
          height="auto"
          tile
        >
          <v-card-title>
            Monitor your assets
          </v-card-title>
          <v-card-text>
            First, you have to select products to monitor. You will be advised when new vulnerabilities are found or a change has been detected by our platform.<br/>
            Select 3 products (max.). Don't panic, it's just a start ;)<br/>
          </v-card-text>
          <v-card-text>
            <v-autocomplete
              v-model="products_autocomplete"
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
          </v-card-text>
          <v-divider></v-divider>
        </v-card>
        <v-btn color="grey" @click="nextStep(2, 'saveMonitoredProducts')">Next<v-icon>mdi-chevron-right</v-icon></v-btn>
        <v-btn @click="nextStep(0)" text>Cancel</v-btn>
      </v-stepper-content>
      <v-stepper-content step="3">
        <v-card
          class="mb-6"
          height="200px"
          tile
        >
          <v-card-title>
            Alert me
          </v-card-title>
          <v-card-text>
            You have successfuly added your products to your monitoring list. Now, let us set a contact email for receiving alerts. Other alert channels are also available (Slack, TheHive, ...) in the 'Settings' page.
            <v-combobox
              v-model="org_settings.alerts_emails"
              clearable
              label="Contact Emails"
              multiple
              :rules="emailRules"
            >
              <template v-slot:selection="{ attrs, item, select, selected }">
                <v-chip
                  v-bind="attrs"
                  :input-value="selected"
                  close
                  @click="select"
                  @click:close="removeContactEmail(item)"
                >
                  <strong>{{ item }}</strong>&nbsp;
                </v-chip>
              </template>
            </v-combobox>
          </v-card-text>
        </v-card>
        <v-btn color="grey" @click="nextStep(3, 'saveAlertEmails')">Next<v-icon>mdi-chevron-right</v-icon></v-btn>
        <v-btn @click="nextStep(1)" text>Cancel</v-btn>
      </v-stepper-content>
      <v-stepper-content step="4">
        <v-card
          class="mb-6"
          height="200px"
          tile
        >
          <v-card-title>
            It's done !
          </v-card-title>
          <v-card-text>
            That's all! You just finished the inital configuration.<br/>
            Want help ? go <a href="/#/help">there</a>
          </v-card-text>
        </v-card>
        <v-btn color="deep-orange" @click="closeMe()">Close<v-icon>mdi-chevron-right</v-icon></v-btn>
        <v-btn @click="nextStep(2)" text>Cancel</v-btn>

      </v-stepper-content>
    </v-stepper>
    <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
      {{ snackText }}
      <v-btn text @click="snack = false">Close</v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import _ from 'lodash';
export default {
  name: "FirstSteps",
  data:() => ({
    stepper_fs: 1,
    steps: 4,
    descriptionLimit: 60,
    products_isLoading: false,
    products_autocomplete: null,
    products_items: [],
    // products_entries: [],
    products_search: null,
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
    ],
    org_settings: {
      alerts_emails: [],
      // alerts_slack: {},
      // alerts_thehive: {},
    },
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  watch: {
    steps(val) {
      if (this.stepper_fs > val) {
        this.stepper_fs = val
      }
    },
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
  mounted() {
  },
  methods: {
    nextStep (n, action="") {
      if (n === this.steps) {
        this.stepper_fs = 1;
      } else {
        this.stepper_fs = n + 1;
      }
      if (action == "saveMonitoredProducts") {
        this.toggleMonitoredProducts();
      }
      if (action == "saveAlertEmails") {
        this.updateContactEmails();
      }
    },
    closeMe(){
      this.$vnode.context.firststeps_overlay = false;
      this.$router.push('/homepage');
    },
    removeSelectedProduct(item) {
      const index = this.products_autocomplete.indexOf(item.name)
      if (index >= 0) this.products_autocomplete.splice(index, 1)
    },
    removeContactEmail(item) {
      this.org_settings.alerts_emails.splice(this.org_settings.alerts_emails.indexOf(item), 1)
      this.org_settings.alerts_emails = [...this.org_settings.alerts_emails]
    },
    toggleMonitoredProducts() {
      var i;
      var j;
      for (i = 0; i < this.products_autocomplete.length; i++) {
        var product_id = this.products_autocomplete[i];
        for (j = 0; j < this.products_items.length; j++) {
          if (this.products_items[j]['id'] == product_id) {
            // save in backend
            let data = {
              'vendor_name': this.products_items[j].vendor,
              'product_name': this.products_items[j].name,
              'monitored': true,
              'organization_id': localStorage.getItem('org_id')
            };
            this.$api.post('/api/monitor/product/toggle', data).then(res => {
              this.loading = false;
              if (res){
                // Snack notifications
                this.snack = true;
                this.snackColor = 'success';
                this.snackText = 'Monitoring status successfuly updated.';
              } else {
                this.snack = true;
                this.snackColor = 'error';
                this.snackText = 'Unable to change the monitoring status';
              }
            }).catch(e => {
              this.loading = false;
              console.log(e);
              return;
            });
          }
        }
      }
    },
    updateContactEmails(){
      var bodyFormData = new FormData();
      bodyFormData.set('org_id', localStorage.getItem('org_id'));
      bodyFormData.set('alerts_emails', this.org_settings.alerts_emails);

      this.$api.post('/users/org/update', bodyFormData).then(res => {
        if (res && res.status != 200) {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to update organization settings :/';
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to update organization settings :/';
      });
    }
  }
};
</script>
