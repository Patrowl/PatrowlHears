from django.core.management.base import BaseCommand
# from data.utils import _import_data
# from common.utils import is_json
from common.utils.constants import DATASYNC_MODELS
import tempfile
import zipfile
import shutil
# import json
import time
import os
# import pprint


class Command(BaseCommand):
    help = 'Import data models from dump files (TGZ > ZIP > JSON)'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--input-archive', type=str, required=True, help='Input archive .tgz', )

    def handle(self, *args, **options):
        start_time = time.time()
        fn = options['input_archive']

        print("Importing data from: '{}'".format(fn))

        if os.path.isfile(fn) is False:
            print("Unable to locate file. Abort captain.")
            return

        #Todo: check extension (tgz || tar.gz)
        with tempfile.TemporaryDirectory() as tmpdirname:
            print("temp folder:", tmpdirname)

            # Unpack files to tmpdir
            shutil.unpack_archive(fn, tmpdirname)

            for zip_file in os.listdir(tmpdirname):
                if not zip_file.endswith(".zip") or not zip_file.startswith(tuple(DATASYNC_MODELS.keys())):
                    continue
                print(zip_file)

                with zipfile.ZipFile(tmpdirname+'/'+zip_file, 'r') as zip_ref:
                    zip_ref.extractall(path=tmpdirname+'/'+zip_file.replace('.zip', ''))

                    print('todo')
                    # time.sleep(9999)

                    # reader = open(fn, 'r')
                    # data = reader.read()
                    # reader.close()
                    #
                    #
                    # # Check file is either a json or a zip file
                    # if is_json(data) is False:
                    #     print("Unable to import data file (invalid JSON format). Abort captain.")
                    #     return
                    #
                    # results = _import_data(json.loads(data), verbose=True)
                    # pprint.pprint(results['stats'])
            # time.sleep(9999999)

        elapsed_time = time.time() - start_time

        print("Import done! Well done captain.")
        print("Elapsed time (in seconds): %.3f" % elapsed_time)
