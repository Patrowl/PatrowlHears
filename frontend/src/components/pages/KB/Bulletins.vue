<template>
  <div>
    <!-- Bulletins Page -->
    <div class="loading" v-if="loading===true">Loading&#8230;</div>
    <v-card>
      <v-card-title>
        Bulletins
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="bulletins.results"
        :options.sync="options"
        :server-items-length="bulletins.count"
        :search="search"
        :footer-props="{
          'items-per-page-options': rowsPerPageItems
        }"
        :loading="loading"
        class="elevation-4"
        item-key="publicid"
        show-select
        multi-sort
      >

      <!-- Summary -->
      <template v-slot:item.title="{ item }">
        <v-clamp autoresize :max-lines="1">
          {{ item.title }}
          <button
            v-if="expanded || clamped"
            slot="after"
            slot-scope="{ toggle, expanded, clamped }"
            class="toggle btn btn-sm"
            @click="toggle"
          >
            {{ ' more' }}
          </button>
        </v-clamp>
      </template>

      <!-- Monitored -->
      <!-- <template v-slot:item.monitored="{ item }">
        <v-chip
          small label outlined color="deep-orange"
          @click="toggleMonitored(item)"
          v-if="item.monitored">Yes</v-chip>
        <v-chip
          small label outlined color="grey"
          @click="toggleMonitored(item)"
          v-if="!item.monitored">No</v-chip>
      </template> -->

      <!-- Modified -->
      <template v-slot:item.published="{ item }">
        <span>{{moment(item.published).format('YYYY-MM-DD')}}</span>
      </template>

      </v-data-table>

      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </v-card>
  </div>
</template>

<script>
import swal from 'sweetalert2';
import VClamp from 'vue-clamp';

export default {
  name: "bulletins",
  components: {
    VClamp
  },
  data: () => ({
    bulletins: [],
    totalbulletins: 0,
    loading: true,
    limit: 20,
    search: '',
    options: {},
    selected: [],
    headers: [
      { text: 'ID', value: 'publicid', width: '150px' },
      { text: 'Vendor', value: 'vendor' },
      { text: 'Title', value: 'title' },
      { text: 'Severity', value: 'severity' },
      // { text: 'Monitored', value: 'monitored', align: 'center' },
      { text: 'Published', value: 'published' },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
    snack: false,
    snackColor: '',
    snackText: '',
  }),
  mounted() {
    // nothing yet
  },
  watch: {
    search: {
      handler(filter) {
        this.search = filter;
        this.options.page = 1;  // reset page count
        this.getDataFromApi();
      },
      deep: true
    },
    options: {
      handler() {
        this.getDataFromApi();
      },
      deep: true
    }
  },

  methods: {
    getDataFromApi() {
      this.loading = true;
      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.options;
        let search = this.search.trim().toLowerCase();

        this.limit = itemsPerPage;
        let items = this.getbulletins(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          this.loading = false;
          resolve({
            items
          });
        }, 300);
      });
    },
    getbulletins(page, itemsPerPage, sortBy, sortDesc) {
      this.loading = true;
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }

      this.$api.get('/api/kb/bulletins?limit='+itemsPerPage+'&page='+page+'&'+sorted_by+'&search='+this.search).then(res => {
        this.bulletins = res.data;
        return this.bulletins;
      }).catch(e => {
        this.bulletins = [];
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get bulletins',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
      this.loading = false;
    },
    toggleMonitored(item) {
      // save in backend
      let data = {'monitored': !item.monitored};
      this.$api.put('/api/kb/bulletin/'+item.id+'/', data).then(res => {
        if (res){
          item.monitored = !item.monitored;
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
        swal.fire({
          title: 'Error',
          text: 'Unable to change the monitoring status',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
        return;
      });
    },
  }
};
</script>
