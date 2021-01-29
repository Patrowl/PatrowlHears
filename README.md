![](https://github.com/Patrowl/PatrowlDocs/blob/master/images/logos/logo-patrowl-light.png)

[![Join the chat at https://gitter.im/Patrowl/Support](https://badges.gitter.im/Patrowl/Support.png)](https://gitter.im/Patrowl/Support)


# **PatrowlHears**
[PatrOwl](https://www.patrowl.io/) provides scalable, free and open-source solutions for orchestrating Security Operations and providing Threat Intelligence feeds. **PatrowlHears** is an advanced and real-time Vulnerability Intelligence platform, including CVE, exploits and threats news.

# Try it now!
To try PatrowlHears, install it by reading the [Installation Guide](https://github.com/Patrowl/PatrowlHears/blob/master/INSTALL.md).

# Architecture
Fully-Developed in Python, PatrowlHears is composed of a backend application using the awesome Django framework and a frontend based on Vue.js + Vuetify. Asynchronous tasks and engine scalability are supported by RabbitMQ and Celery.
PatrowlHears features and data are reachable using the embedded WEB interface or using the REST-API.

# Side projects
- [PatrowlHearsData](https://github.com/Patrowl/PatrowlHearsData): Contains data-scrapper scripts collecting CVE, CPE, CWE and exploit references (cf. CVE-SEARCH project) + raw data as JSON files
- [PatrowlHears4py](https://github.com/Patrowl/PatrowlHears4py): Python CLI and library for PatrowlHears API.

# License
PatrowlHears is an open source and free software released under the [AGPL](https://github.com/Patrowl/PatrowlHears/blob/master/LICENSE) (Affero General Public License). We are committed to ensure that PatrowlHears will remain a free and open source project on the long-run.

# Updates
Information, news and updates are regularly posted on [Patrowl.io Twitter account](https://twitter.com/patrowl_io).

# Contributing
Please see our [Code of conduct](https://github.com/Patrowl/PatrowlDocs/blob/master/support/code_of_conduct.md). We welcome your contributions. Please feel free to fork the code, play with it, make some patches and send us pull requests via [issues](https://github.com/Patrowl/PatrowlHears/issues).

# Roadmap
TBD

# Support
Please [open an issue on GitHub](https://github.com/Patrowl/PatrowlHears/issues) if you'd like to report a bug or request a feature. We are also available on [Gitter](https://gitter.im/PatrowlHears/Support) to help you out.

If you need to contact the project team, send an email to <getsupport@patrowl.io>.

# Pro Edition available in SaaS and on-premise
A commercial Pro Edition is available and officially supported by the PatrOwl company. It includes following extra and awesome engines:
- [x] PatrOwl CSIRT feeds, managed by qualified Cyber-Threat Intelligence analysts
- [x] Terraform+Ansible deployment scripts
- [x] Official Pro Support
- [ ] 3rd party authentication: Azure Active Directory, ADFS (Windows 2012 and 2016), LDAP (WIP)
- [ ] Ticketing system integration, including JIRA, ServiceNow, ZenDesk and GLPI (WIP)

**PatrowlHears** is available on the official PatrOwl SaaS platform or on-premise.
See: https://patrowl.io/products/hears

# Commercial Services
Looking for advanced support, training, integration, custom developments, dual-licensing ? Contact us at getsupport@patrowl.io

# Security contact
Please disclose any security-related issues or vulnerabilities by emailing security@patrowl.io, instead of using the public issue tracker.

# Copyright
Copyright (C) 2020-2021 Nicolas MATTIOCCO ([@MaKyOtOx](https://twitter.com/MaKyOtOx) - nicolas@patrowl.io)

# Travis build status
| Branch  | Status  |
|---|---|
| master | [![Build Status](https://travis-ci.com/Patrowl/PatrowlHears.svg?branch=master)](https://travis-ci.com/Patrowl/PatrowlHears) |
| develop | [![Build Status](https://travis-ci.com/Patrowl/PatrowlHears.svg?branch=develop)](https://travis-ci.com/Patrowl/PatrowlHears) |
