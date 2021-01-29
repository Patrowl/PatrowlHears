from django.core.management.base import BaseCommand
# from celery import group
# from common.utils import chunks
# from data.tasks import import_cpe_task
# from cves.models import Vendor, Product, CPE
from common.feeds.vulns import import_cpes
import time
import os
import json
# from tqdm import tqdm

# CHUNK_SIZE = 32


class Command(BaseCommand):
    help = 'Import CPE from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input-file', type=str, help='Input file', )

    def handle(self, *args, **options):
        start_time = time.time()
        input_file = options['input_file']

        if options['input_file'] in [None, ''] or os.path.exists(input_file) is False:
            print("Unable to locate directory. Abort captain. ABORT !")
            return

        print("Importing data from: '{}'".format(input_file))

        # cpes_sigs = []
        with open(input_file, 'r') as f:
            data = json.load(f)
            import_cpes(data['cpes'])
        #
        #     my_cpes = list(CPE.objects.values_list('vector', flat=True))
        #
        #     for vendor_name in tqdm(data['cpes'].keys(), desc="CPE-pre"):
        #         vendor, inv = Vendor.objects.get_or_create(name=vendor_name)
        #
        #         for product_name in data['cpes'][vendor_name].keys():
        #             product, inp = Product.objects.get_or_create(name=product_name, vendor=vendor)
        #
        #             for cpe_vector in data['cpes'][vendor_name][product_name].keys():
        #                 # if cpe_vector not in my_cpes:
        #                 cpes_sigs.append(
        #                     import_cpe_task.s(cpe_vector, data['cpes'][vendor_name][product_name][cpe_vector], product.id, vendor.id).set(queue='data')
        #                 )
        #                 my_cpes.append(cpe_vector)
        #
        # pbar = tqdm(total=len(cpes_sigs), desc="CPE-run")
        # for chunk in chunks(cpes_sigs, CHUNK_SIZE):
        #     res = group(chunk)()
        #     res.get()
        #     pbar.update(CHUNK_SIZE)
        # pbar.close()

        elapsed_time = time.time() - start_time
        print("Import done! Well done captain.")
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
