from django.core import management as dj_cmd
from django.core.management.base import BaseCommand
import time
import os


class Command(BaseCommand):
    help = 'Import vulns (wrapped)'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--base-dir', type=str, help='Input base directory',)
        parser.add_argument('--all', action='store_true', help='Sync CWEs,CPEs,CVEs,VIAs',)
        parser.add_argument('--cwes', action='store_true', help='Sync CWEs',)
        parser.add_argument('--cpes', action='store_true', help='Sync CPEs',)
        parser.add_argument('--cves', action='store_true', help='Sync CVEs',)
        parser.add_argument('--vias', action='store_true', help='Sync CVE VIAs',)
        # parser.add_argument('--exploits', action='store_true', help='Sync Exploit metadata feeds',)
        # parser.add_argument('--threats', action='store_true', help='Sync Threat metadata feeds',)
        parser.add_argument('-y', '--year', type=str, help='CVEs from Year',)
        parser.add_argument('-l', '--last-update', type=str, help='Last update date (YYYY-MM-DD)',)

    def handle(self, *args, **options):
        start_time = time.time()
        base_dir = options['base_dir']

        print("Importing data from dir: '{}'".format(base_dir))
        # Validate options
        if base_dir in [None, ''] or os.path.isdir(base_dir) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return

        if options['all'] is True or options['cwes'] is True:
            print("[+] Importing CWEs")
            dj_cmd.call_command('importcwes', input_file=base_dir+"CWE/data/cwes.json")

        if options['all'] is True or options['cpes'] is True:
            print("[+] Importing CPEs")
            dj_cmd.call_command('importcpes', input_file=base_dir+"CPE/data/cpes.json")

        if options['all'] is True or options['cves'] is True:
            print("[+] Importing CVEs")
            dj_cmd.call_command('importcves', input_dir=base_dir+"CVE/data", year=options['year'], last_update=options['last_update'])

        if options['all'] is True or options['vias'] is True:
            print("[+] Importing VIAs")
            dj_cmd.call_command('importvias', input_file=base_dir+"VIA/data/via.json", year=options['year'], last_update=options['last_update'])

        elapsed_time = time.time() - start_time
        print("Import done! Well done captain.")
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
