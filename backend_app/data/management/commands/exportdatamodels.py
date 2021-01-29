from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
from data.utils import _export_data_model, _export_data_info_model
from common.utils import _json_serial
from common.utils.constants import DATASYNC_MODELS
from common.utils.zip import zipdir
import zipfile
import datetime
import json
import time
import os
import tempfile

DEFAULT_OUTPUT_DIR = 'var/dump'


class Command(BaseCommand):
    help = 'Dump data from base referential'

    def add_arguments(self, parser):
        # parser.add_argument('-l', '--limit', type=int, help='Limit of results per table', )
        parser.add_argument('-s', '--since', type=str, help='Search updates from date (format: YYYY-MM-DD). Default is one day ago.', )
        parser.add_argument('-t', '--to', type=str, help='Search updates to date (format: YYYY-MM-DD). Default is now.', )
        parser.add_argument('-c', '--chunk-size', type=str, help='Chunk size. Default is defined in Settings.', )
        # parser.add_argument('-f', '--format', type=str, default='zip', help='Data format (json or zip). Default is zip.', )
        parser.add_argument('-o', '--output-file', type=str, help='Output file (no extension).', )
        parser.add_argument('-d', '--output-dir', type=str, help='Output dir. Default id current directory', )

    def handle(self, *args, **options):
        # Output directory
        if options['output_dir'] is not None:
            if os.path.exists(options['output_dir']) is False:
                os.mkdir(options['output_dir'])
            output_dir = options['output_dir']
        else:
            output_dir = DEFAULT_OUTPUT_DIR

        if options['chunk_size'] is None:
            chunk_size = int(settings.HEARS_DATASYNC_CHUNKSIZE)
        else:
            chunk_size = int(chunk_size)

        # Start the timer
        start_time = time.time()

        for model_name in ['kb_cwe', 'kb_cpe', 'kb_cve', 'kb_vendor', 'kb_product', 'kb_product_version', 'vulns', 'exploits', 'threats']:
            print("[+] Dump model '{}'".format(model_name))

            # Create a tmp dir
            with tempfile.TemporaryDirectory() as tmpdirname:
                print(tmpdirname)

                # Collect data model info
                infos = _export_data_info_model(
                    model_class=apps.get_model(DATASYNC_MODELS[model_name]),
                    model_name=model_name,
                    since=options['since'],
                    to=options['to'],
                    from_id=None
                )

                from_id = infos[model_name]['oldest_id']

                has_more_updates = True
                while has_more_updates:
                    data = _export_data_model(
                        model_class=apps.get_model(DATASYNC_MODELS[model_name]),
                        model_name=model_name,
                        since=options['since'],
                        to=options['to'],
                        from_id=from_id,
                        chunk_size=chunk_size,
                    )

                    with open("{}/{}-{}-{}.json".format(tmpdirname, model_name, from_id, data['last_id']), 'w') as fp:
                        json.dump(data, fp, default=_json_serial)

                    # if count < chunk_size: no more updates should be available
                    if data['count'] < chunk_size:
                        has_more_updates = False

                    from_id = data['last_id']

                # Create a zip file
                zipf = zipfile.ZipFile('{}/{}-{}.zip'.format(output_dir, model_name, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]), 'w', zipfile.ZIP_DEFLATED)
                zipdir(tmpdirname, zipf)
                zipf.close()

        elapsed_time = time.time() - start_time
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
