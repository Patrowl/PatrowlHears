from django.core.management.base import BaseCommand
from common.feeds.vulns import sync_exploits_fromvia
from data.tasks import import_via_task
from common.utils import chunks
from celery import group
import time
import os
import json
import re
from tqdm import tqdm

CHUNK_SIZE = 32


class Command(BaseCommand):
    help = 'Import VIA cross-references from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input-file', type=str, help='Input file',)
        parser.add_argument('-y', '--year', type=str, help='CVEs from Year',)
        parser.add_argument('-l', '--last-update', type=str, help='Last update date (YYYY-MM-DD)',)

    def handle(self, *args, **options):
        start_time = time.time()
        input_file = options['input_file']

        if options['input_file'] in [None, ''] or os.path.exists(input_file) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return

        print("Importing data from: '{}'".format(input_file))

        files_sig = []

        with open(input_file, 'r') as f:
            data = json.load(f)
            for cve_id in tqdm(data["cves"].keys(), desc="VIA-pre"):

                try:
                    if options['year'] not in [None, ''] and re.match(r'.*([1-3][0-9]{3})', options['year']) is not None and options['year'] != cve_id.split('-')[1]:
                        continue
                    # sync_exploits_fromvia(cve_id, data["cves"][cve_id])
                    files_sig.append(import_via_task.s(cve_id, data["cves"][cve_id]).set(queue='data'))
                except Exception:
                    pass

        pbar = tqdm(total=len(files_sig), desc="VIA-run")
        for chunk in chunks(files_sig, CHUNK_SIZE):
            res = group(chunk)()
            res.get()
            pbar.update(CHUNK_SIZE)
        pbar.close()

        elapsed_time = time.time() - start_time
        print("Import done! Well done captain.")
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
