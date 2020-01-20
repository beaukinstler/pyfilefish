import os
from settings import *
from filetypes import FilePropertySet
from pyfi_util import pyfish_util as pfu
import codecs
import json

def setup_tests():
    previous_env = os.environ["FLASK_ENV"]
    try:
        #this may be set in the environment
        # but setting here to be sure
        os.environ["FLASK_ENV"] = "testing"
        volume_name = 'Pytest_Test_Files'
        # use the first option in the settings
        type_of_volume = VOLUME_TYPES[0]
        folder = getenv('FISHING_FOLDER')
        file_types = FilePropertySet()
        file_list:dict = {} # if not load_external else pfu.load_pyfish_data()
        pfu.scan_for_files(
            file_list,
            folder=folder,
            file_types=file_types,
            volume_name=volume_name,
            sync_to_s3=False,
            sync_to_local_drive=False,
            load_external=False,
            local_target= None,
            type_of_volume=type_of_volume,
        )

        with codecs.open(JSON_FILE_PATH, "w+", encoding="utf-8") as json_out:
            json_out.write(
                json.dumps(file_list, sort_keys=True, ensure_ascii=False)
            )

        stats = pfu.build_stats_dict(file_list)
        with codecs.open(JSON_STATS_PATH, "w+", encoding="utf-8") as json_out:
            json_out.write(
                json.dumps(stats, sort_keys=True, ensure_ascii=False)
            )

        multiple_files_collection = pfu.build_multiple_dict(file_list)
        if multiple_files_collection:
            with codecs.open(
                JSON_MULTI_SUMMARY_FILE, "w+", encoding="utf-8"
            ) as json_out:
                json_out.write(
                    json.dumps(
                        multiple_files_collection,
                        sort_keys=True,
                        ensure_ascii=False,
                    )
                )

    except:
        # try was really for the finally
        pass


    finally:
        # after this is all done, set the env back
        os.environ["FLASK_ENV"] = previous_env