EXPLOIT_AVAILABILITY = (
    ('unknown', 'No known exploit available'),
    ('private', 'A private exploit is available'),
    ('public', 'A public exploit is available')
)

TRUST_LEVELS = (
    ('unknown', 'Unknown'),
    ('low', 'Low'),         # Not tested
    ('medium', 'Medium'),   # Not tested
    ('high', 'High'),    # Official source, validated by trusted partners
)

TLP_LEVELS = (
    ('white', 'White'),  # Public
    ('green', 'Green'),  # Internal, could be shared
    ('amber', 'Amber'),  # Internal, shareable with members of their own organization who need to know
    ('red', 'Red'),      # Internal, restrictly shareable
    ('black', 'Black'),      # Internal, restrictly shareable
)

EXPLOIT_TYPES = (
    ('unknown', 'Unknown'),
    ('discovery', 'Discovery'),
    ('exploitation', 'Exploitation'),
)

EXPLOIT_MATURITY_LEVELS = (
    ('unknown', 'Unknown'),
    ('unproven', 'Unproven'),
    ('poc', 'PoC'),
    ('functional', 'Functional Exploit'),
)

EXPLOIT_RELEVANCY_RATES = {
    'EXPLOIT_AVAILABILITY': {
        'unknown': 0,
        'private': 0.66,
        'public': 1.5
    },
    'TRUST_LEVELS': {
        'unknown': 0,
        'low': 0.33,
        'medium': 0.66,
        'high': 1,
        'trusted': 1
    },
    'EXPLOIT_MATURITY_LEVELS': {
        'unknown': 0,
        'unproven': 0.5,
        'poc': 1,
        'functional': 1.5
    },
}

DATASYNC_STATUS = (
    ('created', 'Created'),
    ('started', 'Started'),
    ('finished', 'Finished'),
    ('failed', 'Failed'),
)

DATASYNC_MODELS = {
    'kb_vendor': 'cves.Vendor',
    'kb_product': 'cves.Product',
    'kb_product_version': 'cves.ProductVersion',
    'kb_bulletin': 'cves.Bulletin',
    'kb_cwe': 'cves.CWE',
    'kb_cpe': 'cves.CPE',
    'kb_cve': 'cves.CVE',
    'vulns': 'vulns.Vuln',
    'exploits': 'vulns.ExploitMetadata',
    'threats': 'vulns.ThreatMetadata'
}

DATASYNC_MODEL_NAMES = (
    ('kb_vendor', 'kb_vendor',),
    ('kb_product', 'kb_product',),
    ('kb_product_version', 'kb_product_version',),
    ('kb_bulletin', 'kb_bulletin',),
    ('kb_cwe', 'kb_cwe',),
    ('kb_cpe', 'kb_cpe',),
    ('kb_cve', 'kb_cve',),
    ('vulns', 'vulns',),
    ('exploits', 'exploits',),
    ('threats', 'threats',),
)

DATA_FEEDS_IMPORT_TYPES = (
    ('vuln', 'Vuln'),
    ('exploit', 'Exploit'),
    ('advisory', 'Advisory'),
)
