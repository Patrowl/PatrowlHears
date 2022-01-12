<template>
  <div>
    <v-row class="py-0 mt-1">
      <v-col cols="12" class="py-0">
        <span class="subtitle-1">Add a new filter</span>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4">
        <!-- Filter -->
        <v-select
          v-model="new_filter.filter"
          hint="Filter"
          :items="filters_options['vulns']"
          item-text="name"
          item-value="attribute"
          label="Select"
          persistent-hint
          return-object
          single-line
          outlined
          dense
          clearable
        ></v-select>
      </v-col>

      <!-- Criteria -->
      <v-col cols="3">
        <v-select
          :disabled="new_filter.filter == ''"
          v-model="new_filter.criteria"
          hint="Criteria"
          :items="new_filter_criterias"
          item-text="text"
          item-value="value"
          label="Criteria"
          persistent-hint
          single-line
          outlined
          dense
        ></v-select>
      </v-col>

      <!-- Value -->
      <v-col cols="4" v-if="this.new_filter.filter.criteria == 'text' || this.new_filter.filter.criteria == 'numeric'">
        <v-text-field
          :disabled="new_filter.filter == '' || new_filter.criteria == null"
          v-model="new_filter.value"
          v-if="this.new_filter.filter.criteria != 'bool'"
          :type="this.new_filter.filter.criteria == 'numeric'?'number':''"
          hint="Value"
          label="..."
          outlined
          dense
          v-on:keyup.enter="addFilter"
        ></v-text-field>
      </v-col>
      <v-col cols="4" v-if="this.new_filter.filter.criteria == 'date'">
        <v-menu
          v-model="new_filter_date_menu"
          :nudge-right="40"
          transition="scale-transition"
          offset-y
          min-width="290px"
        >
          <template v-slot:activator="{ on, attrs }">
            <v-text-field
              v-model="new_filter_date"
              append-icon="mdi-calendar"
              v-bind="attrs"
              v-on="on"
              outlined
              dense
            ></v-text-field>
          </template>
          <v-date-picker
            v-model="new_filter.value"
            @input="new_filter_date_menu = false"
          ></v-date-picker>
        </v-menu>
      </v-col>

      <!-- Add button -->
      <v-col cols="1">
        <v-btn
          :disabled="(new_filter.value == '' && new_filter.filter.criteria != 'bool') || new_filter.criteria == null"
          fab small outlined
          color="deep-orange"
          @click="addFilter"
          title="Add new filter"
          class="mt-0"
          ><v-icon>mdi-plus</v-icon>
        </v-btn>
      </v-col>
    </v-row>

    <v-row class="pt-2">
      <v-col cols="12" class="py-0" v-if="filters.length > 0">
        <span class="subtitle-1">Applied filters:</span>
      </v-col>
      <v-col cols="12" class="py-0" v-else>
        <span class="subtitle-2 font-italic">No filter applied yet</span>
      </v-col>
    </v-row>
    <v-row v-for='(f, index) in filters' :key="index" align="center">
      <v-col cols="auto">
        <v-icon @click="removeFilter(index)">mdi-delete-outline</v-icon>
      </v-col>
      <v-col cols="4">
        <v-select
          v-model="f.filter"
          :items="filters_options[scope]"
          item-text="name"
          item-value="attribute"
          return-object
          single-line
          outlined
          dense
          hide-details
        ></v-select>
      </v-col>
      <v-col cols="3">
        <v-select
          v-model="f.criteria"
          :items="criterias[f.filter.criteria]"
          item-text="text"
          item-value="value"
          single-line
          outlined
          dense
          hide-details
        ></v-select>
      </v-col>
      <v-col cols="4">
        <v-text-field
          v-model="f.value"
          v-if="f.filter.criteria != 'bool'"
          outlined
          dense
          hide-details
        ></v-text-field>
      </v-col>
    </v-row>
    <v-row align="start" justify="start">
      <v-col>
        <v-btn
          color="deep-orange"
          :disabled="filters.length == 0"
          small
          class="mr-2"
          @click="applySearchFilters">Search</v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import moment from 'moment';

export default {
  name: "AdvancedSearch",
  props: {
    scope: {
      type: String,
      default: 'vulns'
    }
  },
  data: () => ({
    new_filter_date: new Date().toISOString().substr(0, 10),
    new_filter_date_menu: false,
    new_filter: { filter: '', criteria: null, value: '' },
    new_filter_criterias: [],
    filters: [],
    filters_options: {
      'vulns': [
        { name: 'CVE', attribute: 'cveid', criteria: 'text'},
        { name: 'Summary', attribute: 'summary', criteria: 'text'},
        { name: 'Score', attribute: 'score', criteria: 'numeric'},
        { name: 'CVSSv2', attribute: 'cvss', criteria: 'numeric'},
        { name: 'CVSSv2 Vector', attribute: 'cvss_vector', criteria: 'text'},
        { name: 'CVSSv3', attribute: 'cvss3', criteria: 'numeric'},
        { name: 'CVSSv3 Vector', attribute: 'cvss3_vector', criteria: 'text'},
        // { name: 'Exploit count', attribute: 'exploit_count', criteria: 'numeric'},
        // { name: 'Is monitored ?', attribute: 'monitored', criteria: 'bool'},
        { name: 'Is exploitable ?', attribute: 'is_exploitable', criteria: 'bool'},
        { name: 'Is confirmed ?', attribute: 'is_confirmed', criteria: 'bool'},
        { name: 'Is in the News ?', attribute: 'is_in_the_news', criteria: 'bool'},
        { name: 'Is in the Wild ?', attribute: 'is_in_the_wild', criteria: 'bool'},
        { name: 'Published at', attribute: 'published', criteria: 'date'},
        // 'product': 'text'
      ]
    },
    criterias: {
      'text': [
          { text: 'Equals', value: ''},
          // { text: 'Not equals', value: 'not_exact'},
          { text: 'Contains', value: 'contains'},
          // { text: 'Not contains', value: 'not_contains'},
          { text: 'Contains (ignore case)', value: 'icontains'},
          // { text: 'Not contains (ignore case)', value: 'not_icontains'},
      ],
      'numeric': [
        { text: 'Equals', value: ''},
        { text: 'Greater than', value: 'gt'},
        { text: 'Greater than or equals', value: 'gte'},
        { text: 'Less than', value: 'lt'},
        { text: 'Less than or equals', value: 'lte'},
      ],
      'date': [
        { text: 'At', value: 'date'},
        { text: 'After', value: 'date__gt'},
        { text: 'After or at', value: 'date__gte'},
        { text: 'Before', value: 'date__lt'},
        { text: 'Before or at', value: 'date__lte'},
      ],
      'bool': [
        { text: 'Yes', value: 'true'},
        { text: 'No', value: 'false'},
      ],
    }
  }),
  mounted() {

  },
  watch: {
    new_filter: {
      handler() {
        this.new_filter_criterias = this.criterias[this.new_filter.filter.criteria]
      },
      deep: true
    },
  },
  computed: {
  },
  methods: {
    addFilter(){
      this.filters.push(this.new_filter);
      this.new_filter = { filter: '', criteria: null, value: '' }
    },
    removeFilter(idx){
      this.filters.splice(idx);
    },
    applySearchFilters(){
      // Format the filters
      let filters_str = '';
      this.filters.forEach(function (f) {
        // console.log(f);
        var f_str = '';
        if (f.filter.criteria == 'bool'){
          f_str = "&"+f.filter.attribute+"="+f.criteria;
        } else if (f.criteria == ''){
          f_str = "&"+f.filter.attribute+"="+f.value;
        } else {
          f_str = "&"+f.filter.attribute+"__"+f.criteria+"="+f.value;
        }
        filters_str += f_str
      });
      // console.log(filters_str)
      this.$emit('advanced_search_filters', filters_str);
    },
  }
};
</script>

<style>

</style>
