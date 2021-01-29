from django.core.management.base import BaseCommand
from data.utils import _export_data

from common.utils import _json_serial
from io import BytesIO
from zipfile import ZipFile
import datetime
import json
import time
import os


class Command(BaseCommand):
    help = 'Dump data from base referential'

    def add_arguments(self, parser):
        parser.add_argument('-l', '--limit', type=int, help='Limit of results per table', )
        parser.add_argument('-s', '--since', type=str, help='Search updates from date (format: YYYY-MM-DD). Default is one day ago.', )
        parser.add_argument('-t', '--to', type=str, help='Search updates to date (format: YYYY-MM-DD). Default is now.', )
        parser.add_argument('-f', '--format', type=str, help='Data format (json or zip). Default is json.', )
        parser.add_argument('-o', '--output-file', type=str, help='Output file (no extension).', )
        parser.add_argument('-d', '--output-dir', type=str, help='Output dir. Default id current directory', )

    def handle(self, *args, **options):
        # Output directory
        if options['output_dir'] and os.path.exists(options['output_dir']):
            output_dir = options['output_dir']
        else:
            output_dir = 'var/dump'

        # Output filename (without extension)
        if options['output_file']:
            exp_filename = '{}/{}'.format(output_dir, options['output_file'])
        else:
            exp_filename = "{}/patrowlhears_datadump_{}".format(output_dir, datetime.datetime.now().strftime("%Y%m%d%H%M%s%f")[:-3])

        # Start the timer
        start_time = time.time()

        data = _export_data(limit=options['limit'], since=options['since'], to=options['to'])

        if options['format'] == 'zip':

            in_memory = BytesIO()
            zip = ZipFile(in_memory, "a")
            zip.writestr("all.json", json.dumps(data, sort_keys=True, default=_json_serial))
            zip.writestr("vulns.json", json.dumps({'vulns': data['vulns']}, sort_keys=True, default=_json_serial))
            zip.writestr("exploits.json", json.dumps({'exploits': data['exploits']}, sort_keys=True, default=_json_serial))
            zip.writestr("threats.json", json.dumps({'threats': data['threats']}, sort_keys=True, default=_json_serial))
            zip.writestr("kb_cwe.json", json.dumps({'kb_cwe': data['kb_cwe']}, sort_keys=True, default=_json_serial))
            zip.writestr("kb_cpe.json", json.dumps({'kb_cpe': data['kb_cpe']}, sort_keys=True, default=_json_serial))
            zip.writestr("kb_cve.json", json.dumps({'kb_cve': data['kb_cve']}, sort_keys=True, default=_json_serial))
            zip.writestr("kb_vendor.json", json.dumps({'kb_vendor': data['kb_vendor']}, sort_keys=True, default=_json_serial))
            zip.writestr("kb_product.json", json.dumps({'kb_product': data['kb_product']}, sort_keys=True, default=_json_serial))
            zip.writestr("kb_product_version.json", json.dumps({'kb_product_version': data['kb_product_version']}, sort_keys=True, default=_json_serial))

            # fix for Linux zip files read in Windows
            for file in zip.filelist:
                file.create_system = 0

            zip.close()

            with open(exp_filename + ".zip", 'wb') as f:
                f.write(in_memory.getbuffer())

            in_memory.close()

        else:

            with open(exp_filename + ".json", 'w') as fp:
                json.dump(data, fp, default=_json_serial)
            # print(data)
        elapsed_time = time.time() - start_time
        print("Dump file generated: '{}'".format(exp_filename))
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
