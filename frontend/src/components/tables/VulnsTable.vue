<template>
  <div>
    <!-- Rating -->
    <template v-slot:item.score="{ item }">
      <v-chip
        :color="getRatingColor(item.score)"
        class="text-center font-weight-bold"
        label

      >{{item.score}}/100</v-chip><br/>
      <span class="text-caption">CVSSv2: {{item.cvss}}</span>
    </template>

    <!-- Summary -->
    <template v-slot:item.summary="{ item }">
      <div class="py-2">
        <div class="pb-2">
          <span class="deep-orange--text font-weight-medium">{{item.cveid}}</span> / PH-{{item.id}}
          <v-btn
            color="deep-orange"
            icon small
            ><v-icon title="View details" @click="viewVuln(item.id)">mdi-arrow-right-bold-circle-outline</v-icon>
          </v-btn>
        </div>
        <div>
          {{ item.summary }}
        </div>
        <v-chip
          v-for="p in item.products" :key="p.id"
          class="vendor-chip"
          label small link
          @click="$router.push({ 'path': '/product/'+p.id });"
          >
          {{ p.vendor }}: <span class="font-weight-bold">{{p.name}}</span>
        </v-chip>
      </div>
    </template>

    <!-- Metadata -->
    <template v-slot:item.metadata="{ item }">
      <!-- Is exploitable -->
      <v-chip
        label link small
        :color="item.exploit_count>0?'deep-orange':'grey'"
        class="font-weight-bold"
        title="Is exploitable?"
      >{{item.exploit_count}}</v-chip>

      <!-- Remotely exploitable -->
      <v-btn
        :color="item.access.vector=='NETWORK'?'deep-orange':'grey'"
        icon small
        ><v-icon title="Is exploitable remotely?">mdi-cloud</v-icon>
      </v-btn>

      <!-- Auth Needed -->
      <v-btn
        :color="item.access.authentication=='NONE'?'deep-orange':'grey'"
        icon small
        ><v-icon title="Require authentication?">mdi-shield-account</v-icon>
      </v-btn>

      <!-- In the News/Wild -->
      <v-btn
        :color="item.is_in_the_news||item.is_in_the_wild?'deep-orange':'grey'"
        icon small
        ><v-icon title="Is in the news or exploited in the wild?">mdi-star</v-icon>
      </v-btn>
    </template>

    <!-- Monitored -->
    <template v-slot:item.monitored="{ item }">
      <v-chip
        small label outlined color="deep-orange"
        class="text-center font-weight-bold"
        @click="toggleMonitoredVuln(item)"
        v-if="item.monitored">Yes</v-chip>
      <v-chip
        small label outlined color="grey"
        class="text-center font-weight-bold"
        @click="toggleMonitoredVuln(item)"
        v-if="!item.monitored">No</v-chip>
    </template>

    <!-- Updated at -->
    <template v-slot:item.updated_at="{ item }">
      <span>{{moment(item.updated_at).format('YYYY-MM-DD, hh:mm')}}</span>
    </template>
  </div>
</template>

<script>
import moment from 'moment';

export default {
  name: "VulnsTable",
  props: ['item'],
  methods: {
    viewVuln(vuln_id) {
      this.$router.push({ 'name': 'VulnDetails', 'params': { 'vuln_id': vuln_id } });
    },
    editVuln(vuln_id) {
      // Todo
    },
    deleteVuln(vuln_id) {
      // Todo
    },
    toggleMonitoredVuln(item) {
      this.$emit('toggle_monitored_vuln', item);
    },
  }
};
</script>

<style>
.v-data-table td, .v-data-table th {
    padding: 0 8px;
}
.v-dialog {
    position: absolute;
    left: 0;
}
.vendor-chip {
  padding-right: 5px;
  padding-left: 5px;
  margin-right: 3px;
}
.v-chip.v-size--small {
  border-radius: 12px;
  font-size: 12px;
  height: 20px;
}
</style>
