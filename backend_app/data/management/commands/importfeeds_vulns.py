from django.core.management.base import BaseCommand
from common.utils import chunks
from celery import group
from data.tasks import import_feedvuln_task
from data.models import DataFeedImport
import time
import os
import re
import json
from tqdm import tqdm
from datetime import datetime

CHUNK_SIZE = 32
CHECKSUMS_FILENAME = 'checksums.md5'


class Command(BaseCommand):
    help = 'Import vulnerabilities from Feeds JSON files'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--input-dir', type=str, help='Input directory', )
        parser.add_argument('-y', '--year', type=str, help='CVEs from Year',)
        parser.add_argument('-l', '--last-update', type=str, help='Last update date (YYYY-MM-DD)',)
        parser.add_argument('-f', '--feeds', type=str, help='Feeds list - comma-separated (Default: all)',)
        parser.add_argument('-c', '--cve', type=str, help='The filename of a specify CVE')
        parser.add_argument('-e', '--enumerate-feeds', action='store_true', help='Just enumerate feeds list',)
        parser.add_argument('-o', '--force', action='store_true', help='Force / Override checksum',)

    def handle(self, *args, **options):
        start_time = time.time()
        input_dir = options['input_dir']
        last_update = None
        allowed_feeds = None

        # Validate options
        if options['input_dir'] in [None, ''] or os.path.isdir(input_dir) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return

        if options['enumerate_feeds'] is True:
            for feed_dirname in os.listdir(input_dir):
                feed_dirname_full = os.path.join(input_dir, feed_dirname, 'data/vulns')
                if os.path.isdir(feed_dirname_full) and feed_dirname not in ['__pycache__']:
                    print(feed_dirname)
            return

        if options['feeds'] not in [None, '']:
            try:
                allowed_feeds = options['feeds'].split(',')
            except Exception:
                print("Bad feeds format (use commas). Abort captain. ABORT !")
                return

        if options['last_update'] not in [None, '']:
            last_update = ""
            try:
                last_update = datetime.strptime(options['last_update'], '%Y-%m-%d')
                print("Only last updates from {}".format(last_update))
            except Exception:
                print("Bad datetime format (Use 'YYYY-MM-DD' instead). Abort captain. ABORT !")
                return

        print("Importing data from: '{}'".format(input_dir))

        # Find vulns
        for feed_dirname in os.listdir(input_dir):
            if allowed_feeds is not None and feed_dirname not in allowed_feeds:
                continue

            print("Checking already submitted files")
            feed_checksums = get_checksums(input_dir, feed_dirname)
            already_imported_files = list(DataFeedImport.objects.filter(hash__in=feed_checksums.keys(), has_error=False, type='vuln', source=feed_dirname.lower()).values_list('filename', flat=True))

            feed_dirname_full = os.path.join(input_dir, feed_dirname)
            feed_datadir = os.path.join(feed_dirname_full, 'data')
            feed_data_files_dir = os.path.join(feed_datadir, 'vulns')
            # Check if folders exists
            if os.path.isdir(feed_dirname_full) and os.path.isdir(feed_datadir) and os.path.isdir(feed_data_files_dir):
                # filenames
                feed_files = []

                for year_dir in os.listdir(feed_data_files_dir):
                    if options['year'] not in [None, ''] and re.match(r'.*([1-3][0-9]{3})', options['year']) is not None and options['year'] != year_dir.split('/')[-1]:
                        continue

                    year_dir_path = os.path.join(feed_data_files_dir, year_dir)

                    # Month in the directory
                    for month_dir in os.listdir(year_dir_path):
                        month_dir_path = os.path.join(year_dir_path, month_dir)

                        # Day in the list directory
                        for day_dir in os.listdir(month_dir_path):
                            day_dir_path = os.path.join(month_dir_path, day_dir)

                            # Vuln in directory
                            for vuln_filename in os.listdir(day_dir_path):
                                if options['force'] is True:
                                    feed_files.append(os.path.join(day_dir_path, vuln_filename))

                                if type(options['cve']) is str:
                                    if options['cve'] in vuln_filename and vuln_filename not in already_imported_files:
                                        feed_files.append(os.path.join(day_dir_path, vuln_filename))
                                    continue

                                if vuln_filename not in already_imported_files:
                                    feed_files.append(os.path.join(day_dir_path, vuln_filename))

                # task signatures
                feed_files_sig = []

                for file in tqdm(feed_files, desc="{}-pre".format(feed_dirname)):
                    try:
                        # Open the file to extract data
                        with open(file, 'r') as f:
                            # Load the json data
                            file_data = json.load(f)
                            # Extract the datetime
                            file_checked_at = datetime.strptime(file_data['checked_at'].split(' ')[0], '%Y-%m-%d')
                            # Check for the update
                            if last_update in [None, ''] or last_update < file_checked_at or options['force'] is True:
                                # Get the filename
                                filename = file.split('/')[-1]
                                # Ge tthe hash
                                filename_hash = get_hash(feed_checksums, filename)
                                if filename_hash is not None or options['force'] is True:
                                    feed_files_sig.append(import_feedvuln_task.s(file_data, filename, get_hash(feed_checksums, filename)).set(queue='data'))

                    except Exception as e:
                        print(file, e)

                pbar = tqdm(total=len(feed_files_sig), desc="{}-run".format(feed_dirname))
                for chunk in chunks(feed_files_sig, CHUNK_SIZE):
                    res = group(chunk)()
                    res.get()
                    pbar.update(CHUNK_SIZE)
                pbar.close()

        elapsed_time = time.time() - start_time
        print("Import done! Well done captain.")
        print("Elapsed time (in seconds): %.3f" % elapsed_time)


def get_checksums(input_dir, feed_dirname):
    chks = {}
    with open(input_dir+CHECKSUMS_FILENAME, 'r') as f:
        for line in f.readlines():
            hash = line.split(' ')[0]
            filename = line.split(' ')[2].replace('\n', '')
            if feed_dirname+'/data/vulns/' in filename:
                chks.update({hash: filename})
    return chks


def get_hash(chks, filename):
    hash = None
    for k in chks.keys():
        if filename in chks[k]:
            return k
    return hash
