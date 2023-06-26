<template>
    <v-container fluid>
      <p class="title">Usage</p>
      <p class="subtitle-1">General information</p>
      <p class="body-2">
        CanPatch is an open-source platform supporting a vulnerability watch process for IT assets (OS, middleware, application, Web CMS, Java/.Net/Node library, network devices, IoT, ...). Vulnerabilities, exploits and threats information are collected from various OSINT feeds.
      </p>
      <p class="subtitle-1">Monitoring</p>
      <p class="body-2">
        Vendors, products, packages and vulnerabilities could be monitored. New data or changes are then identified and reported to users. Be careful when enabling/disabling monitoring on a vendor. Monitoring will be enabled/disabled on all related products, regardless of previous monitoring status.
      </p>
      <p class="subtitle-1">Organizations</p>
      <p class="body-2">
        An organization (or "Team") is a group of users sharing lists of monitored vendors, products, packages or vulnerabilities. An user could be member of several organizations. An user is able to add and edit exploits or threats references. These submissions remain private within the context of the organization.
      </p>
      <p class="subtitle-1">Alerting</p>
      <p class="body-2">
        Alerts could be sent on key events like changes in monitored assets or periodic reporting.
        Several notification systems could be enabled depending of your configuration, including email, Slack and Feedly. Contacts and endpoints are configured <a href="#/settings">here</a>.
      </p>
      <p class="subtitle-1">REST-API</p>
      <p class="body-2">
        All features and data are available through REST-API using JWT or Token header authentication. See <a href="/api/docs/swagger">Swagger</a>, <a href="/api/docs/redoc">ReDoc</a> and <a href="/api/docs/swagger/?format=openapi">JSON OpenAPI</a> for details. A throttling policy is set on API for preventing abuses.
        API tokens could be created, renewed or deleted in the Settings menu.
      </p>
      <p class="body-2">
        Example:<br/>
        <code>curl 'https://hears.patrowl.io/api/vulns/' -H 'Authorization: Token e36700fd50c1eab4cfef08936ff7421b093c13bb'</code>
      </p>


      <p class="title">Updates</p>
      <p class="body-2">
        Information, news and updates are regularly posted on Canaris.in <a href="https://twitter.com/canaris_india" target="_blank">Twitter</a> account. <!-- and on the <a href="https://blog.patrowl.io" target="_blank">Blog</a>. -->
      </p>

      <p class="title">Contributing</p>
      <p class="body-2">
        CanPatch is an open-source project. All users and contributors are part of the Patrowl's community. We welcome your contributions. Please feel free to fork the code, play with it, make some patches and send us pull requests via issues.
      </p>

      <p class="title">More questions ?</p>
      <p class="body-2">
        Feel free to reach us in your prefered manner:<br/>
        - Send an email at <a href="mailto:getsupport@canaris.in">getsupport@canaris.in</a><br/>
        - Fill an issue on <a href="https://github.com/canaris-in/CanPatch/issues" target="_blank">GitHub</a><br/>
        - Chat on <a href="https://gitter.im/CanPatch/Support" target="_blank">Gitter CanPatch/Support</a>
      </p>

      <p class="title">Copyright</p>
      <p class="body-2">
        Copyright (C) 2020-{{ new Date().getFullYear() }} Patrowl SAS
      </p>

      <p class="title">Version</p>
      <p class="body-2">
        {{app_version}}
      </p>
    </v-container>
</template>

<script>
import AppVersion from '../../../VERSION.json';

export default {
  name: "Help",
  data:() => ({
    app_version: '1.0.0-RC1',
  }),
  mounted() {
    this.app_version = AppVersion.version;
  },
  methods: {
  }
};
</script>
