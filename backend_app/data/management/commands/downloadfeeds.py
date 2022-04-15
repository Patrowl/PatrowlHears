from django.core import management as dj_cmd
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from botocore.client import Config
import tarfile
import os
import tqdm

BUCKET_NAME = "patrowlhears"
FEEDS_FILENAME = "PatrowlHearsDataPro-latest.tgz"


def hook(t):
    def inner(bytes_amount):
        t.update(bytes_amount)
    return inner


class Command(BaseCommand):
    help = 'Download private feeds (vulns, exploits, advisories)'

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output-dir', type=str, help='Output directory',)

    def handle(self, *args, **options):
        output_dir = options['output_dir']

        print("-> Checking destination dir: '{}'".format(output_dir))
        # Validate options
        if output_dir in [None, ''] or os.path.isdir(output_dir) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return
        print("passed!")

        print("-> Checking access/secret keys from configuration")
        if settings.PRO_FEEDS_ACCESS_KEY in [None, ''] or settings.PRO_FEEDS_SECRET_KEY in [None, '']:
            print("Bad feeds credentials (access/secret key). Abort captain. ABORT !")
            return
        print("passed!")

        print("-> Checking endpoint from configuration")
        if settings.PRO_FEEDS_ACCESS_KEY in [None, ''] or settings.PRO_FEEDS_SECRET_KEY in [None, '']:
            print("Bad feeds credentials (access/secret key). Abort captain. ABORT !")
            return
        print("passed!")

        print("-> Downloading latest updates from Hears feeds")
        s3_download = boto3.client(
            's3',
            aws_access_key_id=settings.PRO_FEEDS_ACCESS_KEY,
            aws_secret_access_key=settings.PRO_FEEDS_SECRET_KEY,
            region_name='eu-west-3',
            config=Config(s3={'addressing_style': 'path'}),
            endpoint_url=settings.PRO_FEEDS_ENDPOINT_URL
        )

        file_object = s3_download.get_object(Bucket=BUCKET_NAME, Key=FEEDS_FILENAME)
        filesize = float(file_object['ResponseMetadata']['HTTPHeaders']['content-length'])
        with tqdm.tqdm(total=filesize, unit='B', unit_scale=True, desc=FEEDS_FILENAME) as t:
            s3_download.download_file(BUCKET_NAME, FEEDS_FILENAME, output_dir+FEEDS_FILENAME, Callback=hook(t))
        print("done!")

        print("-> Extracting feeds from archive")
        # tar = tarfile.open(output_dir+FEEDS_FILENAME, "r:gz")
        # tar.extractall(path=output_dir+'/_ext/')
        # tar.close()
        with tarfile.open(output_dir+FEEDS_FILENAME, "r:gz") as tar:
            for member in tqdm.tqdm(iterable=tar.getmembers(), total=len(tar.getmembers())):
                tar.extract(member=member, path=f"{output_dir}/_ext/")
        print("done!")

        print("-> Importing vulns")
        dj_cmd.call_command('importfeeds_vulns', input_dir=output_dir+"_ext/PatrowlHearsDataPro/feeds/")
        print("done!")

        print("-> Importing exploits")
        dj_cmd.call_command('importfeeds_exploits', input_dir=output_dir+"_ext/PatrowlHearsDataPro/feeds/")
        print("done!")

        print("Update finished! Let's roll!")
