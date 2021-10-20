Front-end
  - [ ] View API ratio
  - [ ] Export/import org exploits and threats (CSV, json)
  - [ ] Settings/Sync: show data sync menu if started in slave mode only
  - [ ] Vuln details: Support edition
  - [ ] Dashboards on monitored items:
    - Publication (90j, 90-30j, 30-7j, <7j)/Vuln severities {l/m/h/c}/

Back-end
  - [ ] Rebuild CVSSv2 score if not available
  - [ ] Monitor security bulletins from vendors
  - [ ] Add personal/org notes on vulnerability and exploit
  - [ ] Edit Vuln/CVE manually


# key persmissions:
  - Monitored vendors/products/vulns: integer
  - Add personal metadata: Exploits,Threats,Notes
  - Create API Token: Yes/No
  - Manage Organization: Yes/No
    * Invite/Remove users
  - Organization members: integer
  - Expose sync data
  - Enable client sync data
  - Manage Alerts
    * Email: Yes/No
    * Slack: Yes/No
    * JIRA: Yes/No
    * ServiceNow: Yes/No
