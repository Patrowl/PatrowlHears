from django.core.management.base import BaseCommand
from data.utils import _import_data
# from data.models import DataSync
from common.utils import is_json
import json
import time
import os
import pprint


class Command(BaseCommand):
    help = 'Import data from dump files'

    def add_arguments(self, parser):
        parser.add_argument('input_filename', type=str, help='Input file name',)

    def handle(self, *args, **options):
        start_time = time.time()
        fn = options['input_filename']

        print("Importing data from: '{}'".format(fn))

        if os.path.isfile(fn) is False:
            print("Unable to locate file. Abort captain.")
            return

        reader = open(fn, 'r')
        data = reader.read()
        reader.close()

        # Check file is either a json or a zip file
        if is_json(data) is False:
            print("Unable to import data file (invalid JSON format). Abort captain.")
            return

        results = _import_data(json.loads(data), verbose=True)
        pprint.pprint(results['stats'])

        elapsed_time = time.time() - start_time

        print("Import done! Well done captain.")
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
