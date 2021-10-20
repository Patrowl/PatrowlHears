<template>
    <div>
      <v-tabs
        left
        background-color="white"
        color="deep-orange accent-4"
      >
        <v-tab>Profile</v-tab>
        <!-- <v-tab v-if="isAdmin() == 'true'">Alerting</v-tab> -->
        <v-tab v-if="isAlertAdmin()">Alerting</v-tab>
        <v-tab v-if="isAdmin() == 'notsupported'">Sync</v-tab>
        <!-- <v-tab v-if="isOrgAdmin() == 'true'">Orgs + Users</v-tab> -->
        <!-- <v-tab v-if="isAdmin() == 'true'">Orgs + Users</v-tab> -->
        <v-tab v-if="isTeamOrgAdmin()">Orgs + Users</v-tab>

        <!-- User Profile -->
        <v-tab-item>
          <v-row>
            <v-col cols="8">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Username</v-list-item-title>
                  <v-list-item-subtitle>{{user_profile.username}}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-content>
                  <v-list-item-title>Email</v-list-item-title>
                  <v-list-item-subtitle>{{user_profile.email}}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Permissions</v-list-item-title>
                  <v-list-item-subtitle v-for='(k, v) in user_profile.profile' :key='v'>
                    {{v}}: <strong>{{k}}</strong>
                  </v-list-item-subtitle>
                </v-list-item-content>
                <!-- <v-list-item-content>
                  <v-list-item-title>API throttling</v-list-item-title>
                  <v-list-item-subtitle>{{user_profile.profile.api_throttle_rate}}</v-list-item-subtitle>
                </v-list-item-content> -->
              </v-list-item>
            </v-col>
            <v-col cols="4">
              <v-card class="ma-2">
                <v-card-title @click='showEditProfileCard=!showEditProfileCard'>
                  Edit user profile <v-icon left>mdi-chevron-double-right</v-icon>
                </v-card-title>
                <v-card-text v-if="showEditProfileCard">
                  <v-text-field
                      v-model="user_profile.username"
                      disabled
                      label="Username"></v-text-field>
                  <v-text-field
                      v-model="user_profile.email"
                      disabled
                      label="Email Address"></v-text-field>
                  <v-text-field
                      v-model="user_profile.first_name"
                      label="First Name"></v-text-field>
                  <v-text-field
                      v-model="user_profile.last_name"
                      label="Last Name"></v-text-field>
                </v-card-text>
                <v-card-actions class="justify-center" v-if="showEditProfileCard">
                  <v-btn color="grey" :loading="loading" @click.native="updateUserProfile" block>
                      <v-icon left dark>mdi-check</v-icon>
                      Update Profile
                  </v-btn>
                </v-card-actions>
              </v-card>
              <v-card class="ma-2">
                <v-card-title  @click='showEditTokenCard=!showEditTokenCard'>
                  Edit API token <v-icon left>mdi-chevron-double-right</v-icon>
                </v-card-title>
                <v-card-text v-if="showEditTokenCard">
                  <v-text-field
                      v-model="user_profile.auth_token"
                      :append-icon="show_authtoken ? 'mdi-eye' : 'mdi-eye-off'"
                      :type="show_authtoken ? 'text' : 'password'"
                      @click:append="show_authtoken = !show_authtoken"
                      label="API Token"></v-text-field>
                </v-card-text>
                <v-card-actions class="justify-center" v-if="showEditTokenCard">
                  <v-btn color="red" :loading="loading" @click.native="deleteUserToken">
                      <v-icon left dark>mdi-delete-outline</v-icon>
                      Delete Token
                  </v-btn>
                  <v-btn color="grey" :loading="loading" @click.native="updateUserToken">
                      <v-icon left dark>mdi-autorenew</v-icon>
                      Renew Token
                  </v-btn>
                </v-card-actions>
              </v-card>
              <v-card class="ma-2">
                <v-card-title @click='showEditPasswordCard=!showEditPasswordCard'>
                  Edit password <v-icon left>mdi-chevron-double-right</v-icon>
                </v-card-title>
                <v-card-text v-if='showEditPasswordCard'>
                  <v-text-field
                      v-model="user_profile_chpwd.oldpassword"
                      :append-icon="showPassword_old ? 'mdi-eye' : 'mdi-eye-off'"
                      :type="showPassword_old ? 'text' : 'password'"
                      @click:append="showPassword_old = !showPassword_old"
                      counter
                      label="Old Password"></v-text-field>
                  <v-text-field
                      v-model="user_profile_chpwd.new_password1"
                      :append-icon="showPassword_new1 ? 'mdi-eye' : 'mdi-eye-off'"
                      :type="showPassword_new1 ? 'text' : 'password'"
                      @click:append="showPassword_new1 = !showPassword_new1"
                      counter
                      label="New Password"></v-text-field>
                  <v-text-field
                      v-model="user_profile_chpwd.new_password2"
                      :append-icon="showPassword_new2 ? 'mdi-eye' : 'mdi-eye-off'"
                      :type="showPassword_new2 ? 'text' : 'password'"
                      @click:append="showPassword_new2 = !showPassword_new2"
                      counter
                      label="New Password (again)"></v-text-field>
                </v-card-text>
                <v-card-actions class="justify-center" v-if='showEditPasswordCard'>
                  <v-btn
                    color="grey"
                    :loading="loading"
                    :disabled="user_profile_chpwd.new_password1 != user_profile_chpwd.new_password2"
                    @click.native="updateUserPassword"
                    block
                    >
                      <v-icon left dark>mdi-check</v-icon>
                      Update Password
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-tab-item>

        <!-- Alerting -->
        <v-tab-item v-if="isAlertAdmin()">
          <v-row>
            <v-col cols="10">
              <v-card>
                <v-card-title>
                  Email alerting
                </v-card-title>
                <v-card-text>
                  <!-- Contact Emails -->
                  <v-layout row wrap class="mx-1">
                    <v-flex xs12 sm12 md12>
                      <v-combobox
                        v-model="org_settings.alerts_emails"
                        clearable
                        label="Contact emails (press Enter to confirm)"
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
                    </v-flex>
                    <v-flex xs12 sm12 md12>
                      <v-checkbox
                        v-model="org_settings.enable_daily_email_report"
                        label="Enable daily report by email on monitored assets"
                        dense hide-details
                      ></v-checkbox>
                    </v-flex>
                    <v-flex xs12 sm12 md12>
                      <v-checkbox
                        v-model="org_settings.enable_weekly_email_report"
                        label="Enable weekly report by email on monitored assets"
                        dense hide-details
                      ></v-checkbox>
                    </v-flex>
                    <v-flex xs12 sm12 md12>
                      <v-checkbox
                        v-model="org_settings.enable_monthly_email_report"
                        label="Enable monthly report by email on monitored assets"
                        dense hide-details
                      ></v-checkbox>
                    </v-flex>
                    <v-flex xs12 sm12 md12>
                      <v-checkbox
                        v-model="org_settings.enable_instant_email_report_exploitable"
                        label="Enable instant report by email on monitored assets when become exploitable"
                        dense hide-details
                      ></v-checkbox>
                    </v-flex>
                    <v-flex xs10 sm10 md10>
                      <v-checkbox
                        v-model="org_settings.enable_instant_email_report_score"
                        label="Enable instant report by email on monitored assets with Score >="
                        dense hide-details
                      ></v-checkbox>
                    </v-flex>
                    <v-flex xs2 sm2 md2>
                      <v-text-field
                        v-model="org_settings.enable_instant_email_report_score_value"
                        type="number"
                        label="Score max value"
                        :rules="rules.score"
                      ></v-text-field>
                    </v-flex>
                    <v-flex xs10 sm10 md10>
                      <v-checkbox
                        v-model="org_settings.enable_instant_email_report_cvss"
                        label="Enable instant report by email on monitored assets with CVSSv2 score >="
                        dense hide-details
                      ></v-checkbox>
                    </v-flex>
                    <v-flex xs2 sm2 md2>
                      <v-text-field
                        v-model="org_settings.enable_instant_email_report_cvss_value"
                        type="number"
                        label="CVSSv2 max value"
                        :rules="rules.cvss"
                      ></v-text-field>
                    </v-flex>
                    <v-flex xs10 sm10 md10>
                      <v-checkbox
                        v-model="org_settings.enable_instant_email_report_cvss3"
                        label="Enable instant report by email on monitored assets with CVSSv3 score >="
                        dense hide-details
                      ></v-checkbox>
                    </v-flex>
                    <v-flex xs2 sm2 md2>
                      <v-text-field
                        v-model="org_settings.enable_instant_email_report_cvss3_value"
                        type="number"
                        label="CVSSv3 max value"
                        :rules="rules.cvss"
                      ></v-text-field>
                    </v-flex>
                  </v-layout>
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    color="deep-orange"
                    :loading="loading"
                    @click.native="updateOrgSettings"
                    >
                      <v-icon left dark>mdi-check</v-icon>
                      Save Changes
                  </v-btn>
                  <v-btn
                    color="deep-orange"
                    :loading="loading"
                    @click.native="sendTestEmail"
                    >
                      <v-icon left dark>mdi-cog</v-icon>
                      Send test email
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
          <v-row v-if="this.org_settings.show_slack_settings">
            <v-col cols="10">
              <v-card>
                <v-card-title>
                  Slack alerting
                </v-card-title>
                <v-card-text>
                  <v-text-field
                    v-model="org_settings.alerts_slack_url"
                    label="Slack Webhook URL"
                    placeholder="Ex: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
                  ></v-text-field>
                  <v-checkbox
                    v-model="org_settings.enable_slack_new_vuln"
                    label="Enable notifications when detecting new vulnerabilities (monitored assets)"
                    dense hide-details
                  ></v-checkbox>
                  <v-checkbox
                    v-model="org_settings.enable_slack_update_vuln"
                    label="Enable notifications when detecting changes in vulnerabilities (monitored assets)"
                    dense hide-details
                  ></v-checkbox>
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    color="deep-orange"
                    :loading="loading"
                    @click.native="updateOrgSettings"
                    >
                      <v-icon left dark>mdi-check</v-icon>
                      Save Changes
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
          <v-row v-if="this.org_settings.show_thehive_settings">
            <v-col cols="10">
              <v-card>
                <v-card-title>
                  TheHive alerting
                </v-card-title>
                <v-card-text>
                  <v-text-field
                    v-model="org_settings.alerts_thehive_url"
                    label="TheHive URL"
                    placeholder="Ex: https://thehive.example.com"
                  ></v-text-field>
                  <v-text-field
                    v-model="org_settings.alerts_thehive_apikey"
                    label="TheHive API Key (token)"
                    type="password"
                  ></v-text-field>
                  <v-checkbox
                    v-model="org_settings.enable_thehive_new_vuln"
                    label="Enable notifications when detecting new vulnerabilities (monitored assets)"
                    dense hide-details
                  ></v-checkbox>
                  <v-checkbox
                    v-model="org_settings.enable_thehive_update_vuln"
                    label="Enable notifications when detecting changes in vulnerabilities (monitored assets)"
                    dense hide-details
                  ></v-checkbox>
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    color="deep-orange"
                    :loading="loading"
                    @click.native="updateOrgSettings"
                    >
                      <v-icon left dark>mdi-check</v-icon>
                      Save Changes
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
          <v-row v-if="this.org_settings.show_misp_settings">
            <v-col cols="10">
              <v-card>
                <v-card-title>
                  MISP alerting
                </v-card-title>
                <v-card-text>
                  <v-text-field
                    v-model="org_settings.alerts_misp_url"
                    label="MISP URL"
                    placeholder="Ex: https://misp.example.com"
                  ></v-text-field>
                  <v-text-field
                    v-model="org_settings.alerts_misp_apikey"
                    label="MISP API Key"
                    type="password"
                  ></v-text-field>
                  <v-checkbox
                    v-model="org_settings.enable_misp_new_vuln"
                    label="Enable notifications when detecting new vulnerabilities (monitored assets)"
                    dense hide-details
                  ></v-checkbox>
                  <v-checkbox
                    v-model="org_settings.enable_misp_update_vuln"
                    label="Enable notifications when detecting changes in vulnerabilities (monitored assets)"
                    dense hide-details
                  ></v-checkbox>
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    color="deep-orange"
                    :loading="loading"
                    @click.native="updateOrgSettings"
                    >
                      <v-icon left dark>mdi-check</v-icon>
                      Save Changes
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-tab-item>

        <!-- Sync -->
        <v-tab-item v-if="isAdmin() == 'notsupported'">
          <v-row>
            <v-col cols="3">
              <v-card
              class="mx-auto"
              >
                <v-subheader>Synchronize data from feed</v-subheader>
                <v-card-text>
                  <v-btn color="deep-orange" :loading="loading" @click.native="syncFromRemote('')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync All from remote
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('kb_vendor')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync Vendor
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('kb_product')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync Product
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('kb_product_version')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync ProductVersion
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('kb_bulletin')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync Bulletin
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('kb_cwe')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync CWE
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('kb_cpe')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync CPE
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('kb_cve')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync CVE
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('vulns')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync Vuln
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('exploits')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync Exploits
                  </v-btn><br/>
                  <v-btn color="light-orange" :loading="loading" @click.native="syncFromRemote('threats')" x-small>
                      <v-icon left dark>mdi-check</v-icon>
                      Sync Threats
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="3">
              <v-card
              class="mx-auto"
              >
                <v-list dense>
                  <v-subheader>Synchronize data from local</v-subheader>
                  <v-list-item-group v-model="async_item" color="primary">
                    <v-list-item
                      v-for="(async_item, i) in async_items"
                      :key="i"
                      @click="callAction(async_item)"
                    >
                      <v-list-item-icon>
                        <v-icon v-text="async_item.icon" color="deep-orange">
                        </v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title
                          v-text="async_item.text"
                          link
                          :to="async_item.to">
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list-item-group>
                </v-list>
              </v-card>
            </v-col>
            <v-col cols="3">
              <v-card
              class="mx-auto"
              >
                <v-list dense>
                  <v-subheader>Synchronize CVEs from year</v-subheader>
                  <v-list-item-group color="primary">
                    <v-list-item
                      v-for="(year, i) in cves_years"
                      :key="i"
                      @click="callAction({to: '/api/kb/cves/async/from/'+year })"
                    >
                      <v-list-item-icon>
                        <v-icon v-text="'mdi-clock'" color="deep-orange">
                        </v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title
                          v-text="year"
                          link
                          >
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list-item-group>
                </v-list>
              </v-card>
            </v-col>
            <v-col cols="3">
              <v-card
              class="mx-auto"
              >
                <v-list dense>
                  <v-subheader>Synchronize CVEs at year</v-subheader>
                  <v-list-item-group color="primary">
                    <v-list-item
                      v-for="(year, i) in cves_years"
                      :key="i"
                      @click="callAction({to: '/api/kb/cves/async/'+year })"
                    >
                      <v-list-item-icon>
                        <v-icon v-text="'mdi-clock'" color="deep-orange">
                        </v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title
                          v-text="year"
                          link
                          >
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list-item-group>
                </v-list>
              </v-card>
            </v-col>
          </v-row>
        </v-tab-item>

        <!-- Orgs & Users -->
        <!-- <v-tab-item  v-if="isOrgAdmin() == 'true'"> -->
        <!-- <v-tab-item v-if="isAdmin() == 'true'"> -->
        <v-tab-item v-if="isTeamOrgAdmin()">
          <!-- Organizations -->
          <v-card>
            <v-card-title>
              Organizations
            </v-card-title>
            <v-data-table
              :headers="orgs_headers"
              :items="orgs.results"
              :options.sync="orgs_options"
              :server-items-length="orgs.count"
              :items-per-page="5"
              :footer-props="{
                'items-per-page-options': rowsPerPageItems
              }"
              :loading="loading"
              class="elevation-4"
              item-key="id"
            >
              <template v-slot:item.is_active="{ item }">
                <v-icon
                  small
                  class="mdi mdi-check-circle"
                  color="green"
                  title="Enable Organization"
                  v-if="item.is_active == true"
                  @click="isAdmin() == 'true'?disableOrg(item):''"
                >
                </v-icon>
                <v-icon
                  small
                  class="mdi mdi-checkbox-blank-circle"
                  color="red"
                  title="Disable Organization"
                  v-if="item.is_active == false"
                  @click="isAdmin() == 'true'?enableOrg(item):''"
                >
                </v-icon>
              </template>

              <template v-slot:item.action="{ item }">
                <v-icon
                  small
                  class="mdi mdi-account-plus"
                  color="green"
                  title="Add user in Organization"
                  v-if="isAdmin() == 'true' || item.name != 'Private'"
                  @click="openInvitationDialog(item.id, item.name)"
                >
                </v-icon>
                &nbsp;
                <v-icon
                  small
                  class="mdi mdi-close-circle"
                  title="Remove Organization"
                  color="red"
                  v-if="isAdmin() == 'true'"
                  @click="removeOrg(item)"
                >
                </v-icon>
              </template>
            </v-data-table>

            <v-dialog v-model="dialog_new_organization" max-width="500px" v-if="isAdmin() == 'true'">
              <template v-slot:activator="{ on }">
                <v-btn absolute dark fab top right color="deep-orange" v-on="on" small>
                  <v-icon small>mdi-plus</v-icon>
                </v-btn>
              </template>
              <v-card>
                <v-card-title>
                  Create new organization
                </v-card-title>
                <v-card-text>
                  <v-container>
                    <v-form ref="form-new-organization">
                      <v-text-field v-model="org_form.name" label="Name"></v-text-field>
                      <v-checkbox v-model="org_form.is_active" label="is active ?"></v-checkbox>
                      <v-divider></v-divider>
                      <v-text-field
                        v-model="org_form.email"
                        label="Email owner"
                        :rules="emailRules"
                        required></v-text-field>
                      <v-btn color="success" @click="createOrg">Save</v-btn>
                      <v-btn color="warning" type="reset">Reset</v-btn>
                    </v-form>
                  </v-container>
                </v-card-text>

                <v-card-actions>
                  <v-spacer></v-spacer>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="dialog_invitation" max-width="500px">
              <!-- <template v-slot:activator="{ on }">
                <v-btn absolute dark fab bottom left color="deep-orange" v-on="on">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </template> -->
              <v-card>
                <v-card-title>
                  Invite people to organization '{{invitation.org_name}}'
                </v-card-title>
                <v-card-text>
                  <v-container>
                    <v-form ref="form-user-invitation">
                      <!-- <v-text-field
                        v-model="invitation.email"
                        label="Emails (separated with comma or 1 per line)"
                        :rules="emailRules"
                        required></v-text-field> -->
                      <!-- <v-checkbox
                        v-model="invitation.is_admin"
                        label="Is admin ?"></v-checkbox> -->

                        <v-textarea
                          v-model="invitation.emails"
                          label="Emails"
                          hint="Users emails separated with comma or 1 per line. 50 emails max"
                          required></v-textarea>


                      <v-btn color="success" @click="addUserToOrg" small>Invite</v-btn>
                      <v-btn color="warning" type="reset" small>Reset</v-btn>
                    </v-form>
                  </v-container>
                </v-card-text>

                <v-card-actions>
                  <v-spacer></v-spacer>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-card>
          <br/>
          <!-- Users -->
          <v-card>
            <v-card-title>
              Organization Users
            </v-card-title>
            <v-data-table
              :headers="users_headers"
              :items="users.results"
              :options.sync="users_options"
              :server-items-length="users.count"
              :items-per-page="20"
              :footer-props="{
                'items-per-page-options': rowsPerPageItems
              }"
              :loading="loading"
              class="elevation-4"
              item-key="id"
            >
              <!-- is admin -->
              <template v-slot:item.is_admin="{ item }">
                <v-icon
                  small
                  class="mdi mdi-shield-check"
                  title="Promote user as Org admin"
                  color="deep-orange"
                  v-if="item.is_admin == true"
                  @click="isAdmin() == 'true'?disableOrgAdmin(item.org_id, item.user, item):''"
                ></v-icon>
                <v-icon
                  small
                  class="mdi mdi-shield-check"
                  title="Demote user from Org admin"
                  color="grey"
                  v-if="item.is_admin == false"
                  @click="isAdmin() == 'true'?enableOrgAdmin(item.org_id, item.user, item):''"
                ></v-icon>
              </template>

              <!-- is active -->
              <template v-slot:item.is_active="{ item }">
                <v-icon
                  small
                  class="mdi mdi-check-circle"
                  color="green"
                  v-if="item.is_active == true"
                ></v-icon>
                <v-icon
                  small
                  class="mdi mdi-checkbox-blank-circle"
                  color="grey"
                  v-if="item.is_active == false"
                ></v-icon>
              </template>

              <!-- Actions -->
              <template v-slot:item.action="{ item }">

                <v-icon
                  small
                  class="mdi mdi-account-box"
                  title="View or Update user"
                  @click="viewUser(item.user)"
                >
                </v-icon>
                <v-icon
                  small
                  class="mdi mdi-account-remove"
                  title="Remove user"
                  color="red"
                  v-if="item.username != user_profile.username"
                  @click="delUserFromOrg(item.org_id, item.user, item)"
                >

                </v-icon>
              </template>
            </v-data-table>
          </v-card>

          <v-dialog v-model="dialog_edituser" max-width="600px">
            <user-edit :user_id="dialog_edituser_user_id"></user-edit>
          </v-dialog>

        </v-tab-item>
      </v-tabs>
      <v-snackbar v-model="snack" :timeout="3000" :color="snackColor">
        {{ snackText }}
        <v-btn text @click="snack = false">Close</v-btn>
      </v-snackbar>
    </div>
</template>

<script>
import router from "../../router";
import Users from "../../common/users";
import UserEdit from '@/components/pages/UserEdit.vue';

export default {
  name: "Settings",
  mixins: [Users],
  components: {
    UserEdit
  },
  data: () => ({
    loading: false,
    showEditProfileCard: false,
    showEditPasswordCard: false,
    showEditTokenCard: false,
    user_profile: {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      last_login: '',
      profile: {
        manage_organization: false,
        manage_alert_email: false,
      },
    },
    user_profile_chpwd: {},
    show_authtoken: false,
    showPassword: false,
    showPassword_old: false,
    showPassword_new1: false,
    showPassword_new2: false,
    rules: {
      password: [
        v => !!v || "Password is required",
        v => (v && v.length > 8) || "The password must be longer than 8 characters",
        v => /(?=.*[A-Z])/.test(v) || 'Must have one uppercase character',
        v => /(?=.*\d)/.test(v) || 'Must have one number',
        v => /([!@$%])/.test(v) || 'Must have one special character [!@#$%]'
      ],
      email: [
        v => !!v || 'E-mail is required',
        v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
      ],
      cvss: [
        v => (v && v >= 0 && v <= 10) || "CVSS score has to be between 0 and 10. Default is 8.0",
      ],
      score: [
        v => (v && v >= 0 && v <= 100) || "Score has to be between 0 and 100. Default is 80",
      ],
    },
    org_settings_default: {
      alerts_emails: [],
      alerts_emails_max: 3,
      enable_email_alert_new_vuln: false,
      enable_email_alert_update_vuln: false,
      enable_daily_email_report: false,
      enable_weekly_email_report: false,
      enable_monthly_email_report: false,
      enable_instant_email_report_exploitable: false,
      enable_instant_email_report_score: false,
      enable_instant_email_report_score_value: 80,
      enable_instant_email_report_cvss: false,
      enable_instant_email_report_cvss_value: 8,
      enable_instant_email_report_cvss3: false,
      enable_instant_email_report_cvss3_value: 8,
      show_slack_settings: true,
      alerts_slack_url: '',
      // alerts_slack_apikey: '',
      enable_slack_new_vuln: false,
      enable_slack_update_vuln: false,
      show_thehive_settings: false,
      alerts_thehive_url: '',
      alerts_thehive_apikey: '',
      enable_thehive_new_vuln: false,
      enable_thehive_update_vuln: false,
      show_misp_settings: false,
      alerts_misp_url: '',
      alerts_misp_apikey: '',
      enable_misp_new_vuln: false,
      enable_misp_update_vuln: false,
    },
    org_settings: {
      alerts_emails: [],
      alerts_emails_max: 3,
      enable_email_alert_new_vuln: false,
      enable_email_alert_update_vuln: false,
      enable_daily_email_report: false,
      enable_weekly_email_report: false,
      enable_monthly_email_report: false,
      enable_instant_email_report_exploitable: false,
      enable_instant_email_report_score: false,
      enable_instant_email_report_score_value: 80,
      enable_instant_email_report_cvss: false,
      enable_instant_email_report_cvss_value: 8,
      enable_instant_email_report_cvss3: false,
      enable_instant_email_report_cvss3_value: 8,
      show_slack_settings: true,
      alerts_slack_url: '',
      // alerts_slack_apikey: '',
      enable_slack_new_vuln: false,
      enable_slack_update_vuln: false,
      show_thehive_settings: false,
      alerts_thehive_url: '',
      alerts_thehive_apikey: '',
      enable_thehive_new_vuln: false,
      enable_thehive_update_vuln: false,
      show_misp_settings: false,
      alerts_misp_url: '',
      alerts_misp_apikey: '',
      enable_misp_new_vuln: false,
      enable_misp_update_vuln: false,
    },
    async_item: 1,
    async_items: [
      { text: 'CWE', icon: 'mdi-clock', to: '/api/kb/cwes/async' },
      { text: 'CPE', icon: 'mdi-clock', to: '/api/kb/cpes/async' },
      { text: 'Bulletins', icon: 'mdi-clock', to: '/api/kb/bulletins/async' },
      { text: 'CVE', icon: 'mdi-clock', to: '/api/kb/cves/async' },
      { text: 'VIA', icon: 'mdi-clock', to: '/api/kb/vias/async' },
      { text: 'Vuln / Scores', icon: 'mdi-clock', to: '/api/vulns/refresh_scores' },
      { text: 'Vuln / Product versions', icon: 'mdi-clock', to: '/api/vulns/refresh_vulnerable_versions' },
    ],
    cves_years: [
      '1999',
      '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
      '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019',
      '2020', '2021'
    ],
    orgs: [],
    orgs_options: {},
    org_selected: '',
    orgs_headers: [
      { text: 'Name', value: 'name' },
      { text: 'Slug', value: 'slug' },
      { text: 'Owner', value: 'owner' },
      { text: 'Users', value: 'nb_users' },
      { text: 'Active', value: 'is_active', align: 'center' },
      { text: 'Actions', value: 'action', align: 'center', sortable: false },
    ],
    dialog_new_organization: false,
    org_form: {
      name: '',
      is_active: true
    },
    // search_orgs: '',
    users: [],
    users_options: {},
    users_headers: [
      { text: 'Organization name', value: 'org_name' },
      { text: 'Username', value: 'username' },
      { text: 'Email', value: 'email' },
      { text: 'Admin ?', value: 'is_admin', align: 'center' },
      { text: 'Active ?', value: 'is_active', align: 'center' },
      { text: 'Actions', value: 'action', align: 'center', sortable: false },
    ],
    invitation: {
      org_name: '',
      org_id: 0,
      email: '',
      emails: '',
      is_admin: false
    },
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
    ],
    // search_users: '',
    rowsPerPageItems: [5, 10, 20, 50, 100],
    dialog_invitation: false,
    dialog_edituser: false,
    dialog_edituser_user_id: 0,
    snack: false,
    snackColor: '',
    snackText: ''
  }),
  mounted() {
    this.getUserProfile();
    this.getOrgSettings();
  },
  watch: {
    orgs_options: {
      handler() {
        this.getDataFromApiOrgs().then(data => {});
      },
      deep: true
    },
    users_options: {
      handler() {
        this.getDataFromApiUsers().then(data => {});
      },
      deep: true
    },
  },
  methods: {
    getDataFromApiOrgs() {
      this.loading = true;

      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.orgs_options;

        this.limit = itemsPerPage;
        let orgs = this.getOrgs(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            orgs
          });
        }, 300);
        this.loading = false;
      });
      this.loading = false;
    },
    getDataFromApiUsers() {
      this.loading = true;

      return new Promise((resolve, reject) => {
        const {
          sortBy,
          sortDesc,
          page,
          itemsPerPage
        } = this.users_options;

        this.limit = itemsPerPage;
        let users = this.getUsers(page, this.limit, sortBy, sortDesc);

        setTimeout(() => {
          resolve({
            users
          });
        }, 300);
        this.loading = false;
      });
      this.loading = false;
    },
    getDataFromApiUserProfile() {
      this.loading = true;

      return new Promise((resolve, reject) => {
        let user_profile_api = this.getUserProfile();

        setTimeout(() => {
          resolve({
            user_profile_api
          });
        }, 300);
        this.loading = false;
      });
      this.loading = false;
    },
    callAction(item) {
      this.$api.get(item.to).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Sync successfuly enqueued.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to sync :/';
        }
      }).catch(e => {
        swal.fire({
          title: 'Error',
          text: 'Unable to call action',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    getOrgs(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = '&sorted_by=-' + sortBy;
        } else {
          sorted_by = '&sorted_by=' + sortBy;
        }
      }
      this.$api.get('/api/orgs/?limit='+itemsPerPage+'&page='+page+sorted_by).then(res => {
        if (res && res.status === 200) {
          this.orgs = res.data;
        }
      }).catch(e => {
        this.orgs = [];
        swal.fire({
          title: 'Error',
          text: 'Unable to get org users',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    getUsers(page, itemsPerPage, sortBy, sortDesc) {
      let sorted_by = '';
      if (sortBy.length > 0) {
        if (sortDesc[0] === true) {
          sorted_by = 'sorted_by=-' + sortBy;
        } else {
          sorted_by = 'sorted_by=' + sortBy;
        }
      }
      this.$api.get('/api/org-users/?limit='+itemsPerPage+'&page='+page+'&'+sorted_by).then(res => {
        if (res && res.status === 200) {
          this.users = res.data;
        }
      }).catch(e => {
        this.users = [];
        swal.fire({
          title: 'Error',
          text: 'Unable to get org users',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    getUserProfile() {
      this.$api.get('/users/profile').then(res => {
        if (res && res.status === 200) {
          this.user_profile = res.data;
        }
      }).catch(e => {
        this.user_profile = {};
        swal.fire({
          title: 'Error',
          text: 'Unable to get user profile',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    isAlertAdmin() {
      return this.user_profile.profile.manage_alert_email;
    },
    isTeamOrgAdmin() {
      if (this.isAdmin() == 'true') return true;
      return this.user_profile.profile.manage_organization;
    },
    updateUserProfile() {
      var bodyFormData = new FormData();
      bodyFormData.set('first_name', this.user_profile.first_name);
      bodyFormData.set('last_name', this.user_profile.last_name);

      this.$api.post('/users/profile/update', bodyFormData).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'User profile updated !';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to update user profile :/';
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to update user profile :/';
      });
    },
    sendTestEmail() {
      this.$api.get('/api/alerts/email/test').then(res => {
        if (res && res.status === 200 && res.data.status == "success") {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Test sent. Check your mailbox !';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to send test email: ' + res.data.reason;
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to send test email';
      });
    },
    updateUserToken() {
      var bodyFormData = new FormData();
      this.$api.get('/users/token/renew').then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.user_profile.auth_token = res.data.token;
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'User\'s API Token updated !';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to update user\'s API Token :/';
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to update user profile :/';
      });
    },
    deleteUserToken() {
      var bodyFormData = new FormData();
      this.$api.get('/users/token/delete').then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.user_profile.auth_token = '';
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'User\'s API Token updated !';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to update user\'s API Token :/';
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to update user profile :/';
      });
    },
    updateUserPassword() {
      var bodyFormData = new FormData();
      bodyFormData.set('old_password', this.user_profile_chpwd.oldpassword);
      bodyFormData.set('new_password1', this.user_profile_chpwd.new_password1);
      bodyFormData.set('new_password2', this.user_profile_chpwd.new_password2);

      this.$api.post('/users/profile/chpwd', bodyFormData).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'User profile updated !';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to update user profile :/';
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to update user profile :/';
      });
    },
    getOrgSettings() {
      var org_id = localStorage.getItem('org_id');
      this.$api.get('/users/org/'+org_id+'/settings').then(res => {
        if (res && res.status === 200) {
          // console.log(res.data)
          for (let key in res.data){
            this.org_settings[key] = res.data[key];
          }
          this.org_settings.alerts_slack_url = res.data['alerts_slack']['url'];
          this.org_settings.enable_slack_new_vuln = res.data['alerts_slack']['new_vuln'];
          this.org_settings.enable_slack_update_vuln = res.data['alerts_slack']['update_vuln'];
        }
      }).catch(e => {
        // console.log(e)
        Object.assign(this.org_settings, this.org_settings_default);
        swal.fire({
          title: 'Error',
          text: 'Unable to get org settings profile',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    updateOrgSettings() {
      var bodyFormData = new FormData();
      bodyFormData.set('org_id', localStorage.getItem('org_id'));
      bodyFormData.set('alerts_emails', this.org_settings.alerts_emails);
      bodyFormData.set('enable_email_alert_new_vuln', this.org_settings.enable_email_alert_new_vuln);
      bodyFormData.set('enable_email_alert_update_vuln', this.org_settings.enable_email_alert_update_vuln);
      bodyFormData.set('enable_daily_email_report', this.org_settings.enable_daily_email_report);
      bodyFormData.set('enable_weekly_email_report', this.org_settings.enable_weekly_email_report);
      bodyFormData.set('enable_monthly_email_report', this.org_settings.enable_monthly_email_report);
      bodyFormData.set('enable_instant_email_report_exploitable', this.org_settings.enable_instant_email_report_exploitable);
      bodyFormData.set('enable_instant_email_report_cvss', this.org_settings.enable_instant_email_report_cvss);
      bodyFormData.set('enable_instant_email_report_cvss_value', this.org_settings.enable_instant_email_report_cvss_value);
      bodyFormData.set('enable_instant_email_report_cvss3', this.org_settings.enable_instant_email_report_cvss3);
      bodyFormData.set('enable_instant_email_report_cvss3_value', this.org_settings.enable_instant_email_report_cvss3_value);
      bodyFormData.set('enable_instant_email_report_score', this.org_settings.enable_instant_email_report_score);
      bodyFormData.set('enable_instant_email_report_score_value', this.org_settings.enable_instant_email_report_score_value);
      bodyFormData.set('alerts_slack_url', this.org_settings.alerts_slack_url);
      // bodyFormData.set('alerts_slack_apikey', this.org_settings.alerts_slack_apikey);
      bodyFormData.set('enable_slack_new_vuln', this.org_settings.enable_slack_new_vuln);
      bodyFormData.set('enable_slack_update_vuln', this.org_settings.enable_slack_update_vuln);
      bodyFormData.set('alerts_thehive_url', this.org_settings.alerts_thehive_url);
      bodyFormData.set('alerts_thehive_apikey', this.org_settings.alerts_thehive_apikey);
      bodyFormData.set('enable_thehive_new_vuln', this.org_settings.enable_thehive_new_vuln);
      bodyFormData.set('enable_thehive_update_vuln', this.org_settings.enable_thehive_update_vuln);
      bodyFormData.set('alerts_misp_url', this.org_settings.alerts_misp_url);
      bodyFormData.set('alerts_misp_apikey', this.org_settings.alerts_misp_apikey);
      bodyFormData.set('enable_misp_new_vuln', this.org_settings.enable_misp_new_vuln);
      bodyFormData.set('enable_misp_update_vuln', this.org_settings.enable_misp_update_vuln);

      this.$api.post('/users/org/update', bodyFormData).then(res => {
        if (res && res.status === 200) {
          // console.log(res.data)
          this.org_settings.alerts_emails = res.data.alerts_emails;
          this.org_settings.enable_email_alert_new_vuln = res.data.enable_email_alert_new_vuln;
          this.org_settings.enable_email_alert_update_vuln = res.data.enable_email_alert_update_vuln;
          this.org_settings.enable_daily_email_report = res.data.enable_daily_email_report;
          this.org_settings.enable_weekly_email_report = res.data.enable_weekly_email_report;
          this.org_settings.enable_monthly_email_report = res.data.enable_monthly_email_report;

          this.org_settings.alerts_slack_url = res.data.alerts_slack_url;
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Organization settings updated !';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to update organization settings :/';
        }
      }).catch(e => {
        this.snack = true;
        this.snackColor = 'error';
        this.snackText = 'Unable to update organization settings :/';
      });
    },
    openInvitationDialog(org_id, org_name) {
      this.invitation.org_id = org_id
      this.invitation.org_name = org_name
      this.dialog_invitation = true;
    },
    addUserToOrg(org_id) {
      this.dialog_invitation = false;
      this.snack = true;
      this.snackColor = 'grey';
      this.snackText = 'Processing user invitation into organization';

      var bodyFormData = new FormData();
      // bodyFormData.set('email', this.invitation.email);
      // bodyFormData.set('is_admin', this.invitation.is_admin);
      bodyFormData.set('emails', this.invitation.emails);
      this.$api.post('/users/'+this.invitation.org_id+'/adduser', bodyFormData).then(res => {
        if (res && res.status === 200 && res.data.status == 'success') {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Invitation(s) successfuly sent to valid email addresses.';
          this.$router.go();
        } else if (res && res.status === 200 && res.data.status == 'error'){
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'An error occured during the invitation: '+  res.data.reason;
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'An error occured during the invitation.';
        }

      }).catch(e => {
        // this.loading = false;
        swal.fire({
          title: 'Error',
          text: 'Unable to add users',
          showConfirmButton: false,
          showCloseButton: false,
          timer: 3000
        });
      });
    },
    async delUserFromOrg(org_id, user_id, item) {
      let confirm = await this.$confirm('Do you really want to delete user ?', { title: 'Warning' });
      if (confirm) {
        this.$api.get('/users/'+org_id+'/delete/'+user_id).then(res => {
          if (res && res.status === 200) {
            let idx = this.users.results.indexOf(item);
            this.users.results.splice(idx, 1);
          }
        });
      }
    },
    disableOrg(org){
      this.$api.get('/users/'+org.id+'/disable').then(res => {
        if (res && res.status === 200) {
          org.is_active = false;
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Organization successfuly disabled.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to disable the Organization.';
        }
      });
    },
    enableOrg(org){
      this.$api.get('/users/'+org.id+'/enable').then(res => {
        if (res && res.status === 200) {
          org.is_active = true;
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Organization successfuly enabled.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to enable the Organization.';
        }
      });
    },
    enableOrgAdmin(org_id, user_id, item){
      this.$api.get('/users/'+org_id+'/'+user_id+'/admin/enable').then(res => {
        if (res && res.status === 200) {
          item.is_admin = true;
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Organization admin successfuly enabled.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to enable the Organization admin.';
        }
      });
    },
    disableOrgAdmin(org_id, user_id, item){
      this.$api.get('/users/'+org_id+'/'+user_id+'/admin/disable').then(res => {
        if (res && res.status === 200) {
          item.is_admin = false;
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Organization admin successfuly disabled.';
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to disable the Organization admin.';
        }
      });
    },
    createOrg(org){
      this.dialog_new_organization = false;
      var bodyFormData = new FormData();
      bodyFormData.set('name', this.org_form.name);
      bodyFormData.set('is_active', this.org_form.is_active);
      bodyFormData.set('email', this.org_form.email);
      this.$api.post('/users/addorg', bodyFormData).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Organization successfuly created.';
          this.$router.go();
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to create the Organization.';
        }
      });
    },
    syncFromRemote(model){
      let sync_url = '/api/data/sync/run';
      if(model != '') {
        sync_url = sync_url + '?model='+model;
      }
      this.$api.get(sync_url).then(res => {
        if (res && res.status === 200) {
          // Snack notifications
          this.snack = true;
          this.snackColor = 'success';
          this.snackText = 'Sync successfuly enqueued.';
          this.$router.go();
        } else {
          this.snack = true;
          this.snackColor = 'error';
          this.snackText = 'Unable to start data sync from remote.';
        }
      });
    },
    async removeOrg(org){
      let confirm = await this.$confirm('Do you really want to delete organization ?', { title: 'Warning' });
      if (confirm) {
        this.$api.get('/users/'+org.id+'/remove').then(res => {
          if (res && res.status === 200) {
            let idx = this.orgs.results.indexOf(org);
            this.orgs.results.splice(idx, 1);
            // Snack notifications
            this.snack = true;
            this.snackColor = 'success';
            this.snackText = 'Organization successfuly removed.';
          } else {
            this.snack = true;
            this.snackColor = 'error';
            this.snackText = 'Unable to remove the Organization.';
          }
        });
      }
    },
    removeContactEmail(item) {
      this.org_settings.alerts_emails.splice(this.org_settings.alerts_emails.indexOf(item), 1)
      this.org_settings.alerts_emails = [...this.org_settings.alerts_emails]
    },
    viewUser(user){
      // console.log(user);
      this.dialog_edituser = true;
      this.dialog_edituser_user_id = user;
    },
    showManageAlertsEmail(){
      return JSON.parse(this.getUserProfile()).manage_alert_email;
    },
    showManageAlertsSlack(){
      return JSON.parse(this.getUserProfile()).manage_alert_slack;
    }
  }
};
</script>

<style>
.v-btn--fab.v-size--small.v-btn--absolute.v-btn--top {
  top: 0px;
}
</style>
