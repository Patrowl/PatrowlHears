EXPLOIT_AVAILABILITY = (
    ('unknown', 'No known exploit available'),
    ('private', 'A private exploit is available'),
    ('public', 'A public exploit is available')
)

TRUST_LEVELS = (
    ('unknown', 'Unknown'),
    ('low', 'Low'),         # Not tested
    ('medium', 'Medium'),   # Not tested
    ('trusted', 'High'),    # Official source, validated by trusted partners
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
