# Purpose: Run a program to utilize the PyfileFish libraries,
#           Looking for files, syncing to a local share, or
#           Remote system like S3
#
import json
import codecs
# from pprint import pprint
# import logging
from pyfi_util import pyfish_util as pfu
# from settings import *
from settings import logger, SYNC_TO_S3, SYNC_TO_LOCAL, LOAD_EXTERNAL, \
    JSON_FILE_PATH, JSON_STATS_PATH, JSON_MULTI_SUMMARY_FILE, \
    FLAT_FILE_DATA_DIR, IGNORE_DIRS, WRITE_OUT_DATA, WRITE_OUT_STATS, \
    WRITE_OUT_MULTI
import pyfi_ui as pui


def say_goodbye():
    print("\nExiting...\n")
    print("Goodbye!\n")
    exit(0)


# MAIN FUNCTION
def main():
    # det defaults and properties
    sync_to_s3 = SYNC_TO_S3
    sync_to_another_drive = SYNC_TO_LOCAL
    load_external = LOAD_EXTERNAL
    json_file_path = JSON_FILE_PATH
    json_stats_path = JSON_STATS_PATH
    json_multi_summary_file = JSON_MULTI_SUMMARY_FILE
    flat_file_data_dir = FLAT_FILE_DATA_DIR
    # flat_file_suffix = "_filefish_out.log"
    target = None
    # get cli user input
    run_mode = pui.prompt_user_for_run_mode()
    if run_mode in [1, 2]:
        say_goodbye()
    if run_mode == 3:
        sync_to_s3 = True
    if run_mode == 4:
        sync_to_another_drive = True
        target = pui.prompt_for_local_dest()
        # shouldn't scan the destination
        dir_to_ignore = target.split("/")[-1]
        IGNORE_DIRS.append(dir_to_ignore)
    elif run_mode == 5:
        volume_name = pui.prompt_for_volume()
        file_types = pui.get_file_types_from_user()
        target = pui.prompt_for_local_dest()
        pfu.only_sync_file(
            local_target=target, volume_name=volume_name, file_types=file_types
        )
        say_goodbye()

    elif run_mode >= 6:
        say_goodbye()

    volume_name = pui.prompt_for_volume()
    folder = pui.prompt_folder_to_scan()
    file_types = pui.get_file_types_from_user()
    file_list = {} if not load_external else pfu.load_pyfish_data()
    pfu.scan_for_files(
        file_list,
        folder=folder,
        file_types=file_types,
        volume_name=volume_name,
        sync_to_s3=sync_to_s3,
        sync_to_local_drive=sync_to_another_drive,
        load_external=LOAD_EXTERNAL,
        local_target=target,
    )

    print(f"End Time: {str(pfu.datetime.datetime.now().time())}")
    print(f"All done.... See {flat_file_data_dir} folder for output files")
    print(
        f"All done.... See {json_file_path} folder\n"
        " for accumulated json data from all sources"
    )

    stats = pfu.build_stats_dict(file_list)

    """re-save the data to a file
    """
    if WRITE_OUT_DATA:
        with codecs.open(json_file_path, "w+", encoding="utf-8") as json_out:
            json_out.write(
                json.dumps(file_list, sort_keys=True, ensure_ascii=False)
            )

    """dump out the stats to a file
    """
    if WRITE_OUT_STATS:
        with codecs.open(json_stats_path, "w+", encoding="utf-8") as json_out:
            json_out.write(
                json.dumps(stats, sort_keys=True, ensure_ascii=False)
            )

    multiple_files_collection = pfu.build_multiple_dict(file_list)
    if WRITE_OUT_MULTI:
        if multiple_files_collection:
            with codecs.open(
                json_multi_summary_file, "w+", encoding="utf-8"
            ) as json_out:
                json_out.write(
                    json.dumps(
                        multiple_files_collection,
                        sort_keys=True,
                        ensure_ascii=False,
                    )
                )


if __name__ == "__main__":
    logger.info(f"{__name__} has started. Logging to {logger.name}")
    main()
