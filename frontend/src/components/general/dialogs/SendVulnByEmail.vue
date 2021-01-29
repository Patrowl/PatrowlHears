<template>
  <v-dialog v-model="show" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Send vulnerability by emaile</span>
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
          <v-btn color="success" @click="sendEmailVuln">Send</v-btn>
          <v-btn color="warning" type="reset">Reset</v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <v-snackbar v-model="snack" :timeout="3000" :color="snackColor" dense>
      {{ snackText }}
      <v-btn text @click="snack = false">Close</v-btn>
    </v-snackbar>
    <!-- <PSnackBar :snack="snack" name="snack"/> -->

  </v-dialog>
</template>

<script>

// import PSnackBar from '@/components/general/PSnackBar.vue';

export default {
  name: "DialogSendVulnByEmail",
  // components: {
  //   PSnackBar
  // },
  props: [
    'vuln_id', 'visible'
  ],
  data: () => ({
    notification_data: {
      'emails': ''
    },
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  mounted() {
  },
  computed: {
    show: {
      get () {
        return this.visible
      },
      set (value) {
        if (!value) {
          this.$emit('close')
        }
      }
    }
  },
  watch: {
  },
  methods: {
    sendEmailVuln() {
      this.$api.post('/api/vulns/'+this.vuln_id+'/export/email', this.notification_data).then(res => {
        // console.log("cousscou")
        this.snack = true;
        this.snackColor = 'success';
        this.snackText = 'Vulnerability details successfuly sent by mail.';
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to send vulnerability details.';
      });
      this.show = false;
    },
  }
};
</script>

<style>
</style>
