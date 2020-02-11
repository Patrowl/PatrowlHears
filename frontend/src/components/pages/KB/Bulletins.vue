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

      <!-- Modified -->
      <template v-slot:item.published="{ item }">
        <span>{{moment(item.published).format('YYYY-MM-DD')}}</span>
      </template>

      </v-data-table>
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
      { text: 'Published', value: 'published' },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
  }),
  mounted() {
    // nothing yet
  },
  watch: {
    search: {
      handler(filter) {
        this.search = filter;
        this.options.page = 1;  // reset page count
        this.getDataFromApi().then(data => {
          // this.bulletins = data.results;
          // this.totalbulletins = data.count;
        });
      },
      deep: true
    },
    options: {
      handler() {
        this.getDataFromApi().then(data => {
          // this.bulletins = data.results;
          // this.totalbulletins = data.count;
        });
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

      this.$api.get('/api/kb/bulletin?limit='+itemsPerPage+'&page='+page+'&'+sorted_by+'&search='+this.search).then(res => {
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
  }
};
</script>
