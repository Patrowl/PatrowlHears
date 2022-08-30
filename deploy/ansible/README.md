# **PatrowlHears Ansible Playbooks**
## Pre-requisites:
- Your brain
- Ansible


## Commands
- Copy and update the sample file `ansible/vars.yml.sample` to `ansible/vars.yml`
```
ansible-playbook patrowlhears.yml -t patrowlhears-install -i myhost,
```

# License
PatrowlHears is an open source and free software released under the [AGPL](https://github.com/Patrowl/PatrowlHears/blob/master/LICENSE) (Affero General Public License). We are committed to ensure that PatrowlHears will remain a free and open source project on the long-run.

# Support
Please [open an issue on GitHub](https://github.com/Patrowl/PatrowlHears/issues) if you'd like to report a bug or request a feature. We are also available on [Gitter](https://gitter.im/Patrowl/Support) to help you out.

If you need to contact the project team, send an email to <getsupport@patrowl.io>.

# Pro Edition available in SaaS and on-premise
A commercial Pro Edition is available and officially supported by the PatrOwl company. It includes following extra and awesome engines:
- [x] Auto-Updated feeds (no need to install and maintain extra tools like CVE-SEARCH)
- [x] PatrOwl CSIRT feeds, managed by qualified Cyber-Threat Intelligence analysts
- [x] Official Pro Support
- [x] 3rd party authentication: Azure Active Directory, ADFS (Windows 2012 and 2016), LDAP (WIP)
- [ ] Ticketing system integration, including JIRA, ServiceNow, ZenDesk and GLPI (WIP)

**PatrowlHears** is available on the official PatrOwl SaaS platform or on-premise.
See: https://patrowl.io/get-started

# Commercial Services
Looking for advanced support, training, integration, custom developments, dual-licensing ? Contact us at getsupport@patrowl.io

# Copyright
Copyright (C) 2022 Nicolas MATTIOCCO ([@MaKyOtOx](https://twitter.com/MaKyOtOx) - nicolas@patrowl.io)

# Travis build status
| Branch  | Status  |
|---|---|
| master | [![Build Status](https://travis-ci.com/Patrowl/PatrowlHears.svg?branch=master)](https://travis-ci.com/Patrowl/PatrowlHears) |
| develop | [![Build Status](https://travis-ci.com/Patrowl/PatrowlHears.svg?branch=develop)](https://travis-ci.com/Patrowl/PatrowlHears) |
