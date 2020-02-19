<template>
  <div>
    Search page - Results for {{this.appsearch}}


    <v-card v-for="result in results">
      <v-card-title v-if="result.type == 'vuln'">
        PHID-{{result.value.id}}
      </v-card-title>
      <v-card-title v-if="result.type == 'exploit'">
        {{result.value.link}}
      </v-card-title>

      <v-card-subtitle v-if="result.type == 'vuln'">
        Vulnerability
      </v-card-subtitle>
      <v-card-subtitle v-if="result.type == 'exploit'">
        Exploit metadata for vulnerability PHID-{{result.value.vuln_id}}
      </v-card-subtitle>
      <v-card-text>
        coucou
      </v-card-text>
      <v-card-actions>
        <v-btn text color="deep-orange accent-4">Explore</v-btn>
      <v-btn text color="deep-gray accent-4">Bookmark</v-btn>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon>mdi-heart</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>mdi-share-variant</v-icon>
      </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import router from "../../router";
export default {
  name: "Search",
  data: () => ({
    results: [],
    totalresults: 0,
    loading: true,
    limit: 20,
    options: {},
    appsearch: '',
    // appsearch: this.$route.params.appsearch
  }),
  beforeRouteUpdate(to) {
    this.appsearch = to.params.appsearch
  },
  mounted() {
    this.appsearch = this.$router.currentRoute.params.appsearch;
  },
  watch: {
    appsearch: {
      handler(filter) {
        this.appsearch = filter;
        // alert("cou");
        this.getDataFromApi();
      }
    }
  },
  computed: {
    search_msg() {
      return `Searching for, ${this.appsearch}!`;
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
        // let search = this.search.trim().toLowerCase();

        this.limit = itemsPerPage;
        let items = this.search_query(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            items
          });
        }, 300);
      });
      this.loading = false;
    },
    search_query(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      // if (sortBy.length > 0) {
      //   if (sortDesc[0] === true) {
      //     sorted_by = '&sorted_by=-' + sortBy;
      //   } else {
      //     sorted_by = '&sorted_by=' + sortBy;
      //   }
      // }
      let search = this.appsearch.trim().toLowerCase();
      this.$api.get('/api/search/'+search+'?limit='+itemsPerPage+'&page='+page+sorted_by).then(res => {
        this.results = res.data;
        console.log(res);
        this.loading = false;
        return this.vulns;
      }).catch(e => {
        this.results = [];
        // this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get results from search query',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        })
      });
    },
  }
};
</script>
