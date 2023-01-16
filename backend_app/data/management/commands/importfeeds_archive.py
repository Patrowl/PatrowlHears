from django.core import management as dj_cmd
from django.core.management.base import BaseCommand
from django.conf import settings
import tarfile
import os
import tqdm

FEEDS_FILENAME = "PatrowlHearsDataPro-latest.tgz"


def hook(t):
    def inner(bytes_amount):
        t.update(bytes_amount)
    return inner


class Command(BaseCommand):
    help = 'Import private feeds (vulns, exploits, advisories) from archive'

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output-dir', type=str, help='Output directory',)
        parser.add_argument('-d', '--file-dir', type=str, required=True, help='File directory',)
        parser.add_argument('-f', '--file-name', type=str, help=f'Archive filename. Default: "{FEEDS_FILENAME}"', default=FEEDS_FILENAME)

    def handle(self, *args, **options):
        output_dir = options['output_dir']

        print("-> Checking destination dir: '{}'".format(output_dir))
        # Validate options
        if output_dir in [None, ''] or os.path.isdir(output_dir) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return
        
        file_dir = options['file_dir']
        print("-> Checking import dir: '{}'".format(file_dir))
        # Validate options
        if file_dir in [None, ''] or os.path.isdir(file_dir) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return
        
        filename = options['file_name']
        filepath = os.path.join(file_dir, filename)
        if os.path.isfile(filepath) is False:
            print(f"Unable to locate file '{filepath}'. Abort captain. ABORT !")
            return
        
        print("-> Extracting feeds from archive")
        with tarfile.open(filepath, "r:gz") as tar:
            for member in tqdm.tqdm(iterable=tar.getmembers(), total=len(tar.getmembers())):
                tar.extract(member=member, path=f"{output_dir}/_ext/")
        print("done!")

        print("-> Importing vulns")
        dj_cmd.call_command('importfeeds_vulns', input_dir=output_dir+"/_ext/PatrowlHearsDataPro/feeds/")
        print("done!")

        print("-> Importing exploits")
        dj_cmd.call_command('importfeeds_exploits', input_dir=output_dir+"/_ext/PatrowlHearsDataPro/feeds/")
        print("done!")

        print("Update finished! Let's roll!")
