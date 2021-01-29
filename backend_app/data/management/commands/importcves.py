from django.core.management.base import BaseCommand
from common.feeds.vulns import import_cve
from data.tasks import import_cve_task
from common.utils import chunks
from celery import group
import time
import os
import json
import re
from tqdm import tqdm
from datetime import datetime


CHUNK_SIZE = 32


class Command(BaseCommand):
    help = 'Import CVE from JSON files'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--input-dir', type=str, help='Input directory',)
        parser.add_argument('-f', '--filename', type=str, help='Input filename',)
        parser.add_argument('-y', '--year', type=str, help='CVEs from Year',)
        parser.add_argument('-l', '--last-update', type=str, help='Last update date (YYYY-MM-DD)',)

    def handle(self, *args, **options):
        start_time = time.time()
        input_dir = options['input_dir']
        last_update = None

        # Validate options
        if options['input_dir'] in [None, ''] or os.path.isdir(input_dir) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return

        if options['last_update'] not in [None, '']:
            print(options['last_update'])
            last_update = ""
            try:
                last_update = datetime.strptime(options['last_update'], '%Y-%m-%d')
                print("Only last updates from {}".format(last_update))
            except Exception:
                print("Bad datetime format (Use 'YYYY-MM-DD' instead). Abort captain. ABORT !")
                return

        print("Importing data from: '{}'".format(input_dir))

        files = []
        files_sig = []
        for root, directories, filenames in os.walk(input_dir):
            for filename in filenames:
                if options['year'] not in [None, ''] and re.match(r'.*([1-3][0-9]{3})', options['year']) is not None and options['year'] != root.split('/')[-1]:
                    continue
                if options['filename'] is None or options['filename'] == filename:
                    files.append(os.path.join(root, filename))

        with tqdm(total=len(files), desc="CVES-pre") as pbar:
            for f in files:
                with open(f, 'r') as json_file:
                    data = json.load(json_file)
                    if last_update is None or datetime.strptime(data['lastModifiedDate'], '%Y-%m-%dT%H:%MZ') >= last_update:
                        # import_cve(data)
                        files_sig.append(import_cve_task.s(data).set(queue='data'))

                pbar.update()

        pbar = tqdm(total=len(files_sig), desc="CVES-run")
        for chunk in chunks(files_sig, CHUNK_SIZE):
            res = group(chunk)()
            res.get()
            pbar.update(CHUNK_SIZE)
        pbar.close()

        elapsed_time = time.time() - start_time
        print("Import done! Well done captain.")
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
