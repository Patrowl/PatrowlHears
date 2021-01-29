<template>
  <div>
    <!-- Product Versions Page -->
    <div class="loading" v-if="loading===true">Loading&#8230;</div>
    <v-card>
      <v-card-title>
        Product Versions for {{this.vendor_name}}
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
        :items="products.results"
        :options.sync="options"
        :server-items-length="products.count"
        :search="search"
        :footer-props="{
          'items-per-page-options': rowsPerPageItems
        }"
        :loading="loading"
        class="elevation-4"
        item-key="product"
        show-select
      >
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import swal from 'sweetalert2';

export default {
  name: "products",
  data: () => ({
    vendor_name: "",
    products: [],
    loading: true,
    limit: 20,
    totalproducts: 0,
    search: '',
    options: {},
    selected: [],
    headers: [
      { text: 'Product', value: 'product' },
      { text: 'Version', value: 'title' },
      { text: 'Vector', value: 'vector' },
    ],
    rowsPerPageItems: [5, 10, 20, 50, 100],
  }),
  mounted() {
    this.vendor_name = this.$router.currentRoute.params.vendor_name;
    this.getDataFromApi();
  },
  watch: {
    search: {
      handler(filter) {
        this.search = filter;
        this.options.page = 1;  // reset page count
        this.getDataFromApi().then(data => {
          //nothin
        });
      },
      deep: true
    },
    options: {
      handler() {
        this.getDataFromApi().then(data => {
          // this.vendors = data.results;
          // this.totalvendors = data.count;
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

        let items = this.getProducts(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          this.loading = false;
          resolve({
            items
          });
        }, 300);
      });
    },
    getProducts(page, itemsPerPage, sortBy, sortDesc) {
      this.loading = true;
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }

      // this.$api.get('/api/kb/vendors/'+this.vendor_name+'/products?product__icontains='+this.search+'&'+sorted_by).then(res => {
      this.$api.get('/api/kb/vendors/'+this.vendor_name+'/products?limit='+itemsPerPage+'&page='+page+'&product__icontains='+this.search+'&'+sorted_by).then(res => {
        this.products = res.data;
        return this.products;
      }).catch(e => {
        this.products = [];
        this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'unable to get products',
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
