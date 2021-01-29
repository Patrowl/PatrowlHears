from django.core.management.base import BaseCommand
from common.feeds.vulns import import_cwes
import time
import os
import json


class Command(BaseCommand):
    help = 'Import CWE from JSON files'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input-file', type=str, help='Input file',)

    def handle(self, *args, **options):
        start_time = time.time()
        input_file = options['input_file']

        if options['input_file'] in [None, ''] or os.path.exists(input_file) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return

        print("Importing data from: '{}'".format(input_file))

        with open(input_file, 'r') as f:
            data = json.load(f)
            import_cwes(data['cwes'])

        elapsed_time = time.time() - start_time
        print("Import done! Well done captain.")
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
