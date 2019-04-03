

# Purpose: get all files ending with a given extension in a drive or folder

import os
from hashlib import md5
import datetime
import json
import codecs
from filetypes import FileProperySet
from pprint import pprint


# Functions to move to another module or class
def get_file_types_from_user():
    """prompt user for file types and return a list
    """
    # fileTypeList = ['png', 'jpeg', 'mp4', 'bmp', 'wav', 'jpg', ]
    filePropList = FileProperySet()
    file_type_input = ""
    while True:
        if file_type_input == 'new':
            # fileTypeList = []
            filePropList.clear()
        # fileTypeList.append(file_type_input)
        prompt_text = "Please input file types to search for, but don't " + \
            "add the period.\n  Enter 'done' if satisfied with - " + \
            ', '.join([ prop.extension for prop in filePropList.ft_list]) + "\n: "
        prompt_text += "Or type 'new' to clear the list and start over\n"
        file_type_input = input(prompt_text)
        if file_type_input == 'done':
            break
        if file_type_input != 'new':
            print("Please enter a mininimum size in bytes."
                    "(smaller files will be ignored.)")
            min_size = input("mininmum size: ")
            filePropList.add(filePropList.file_properties(file_type_input, min_size))

    # return fileTypeList
    return filePropList


#
def modification_date(filename):
    time_of_mod = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(time_of_mod)


# for getting the hex version of md5
def get_md5(fileObjectToHash, block_size=(2048*20)):
    file_hash = md5()
    while True:
        data = fileObjectToHash.read(block_size)
        if not data:
            break
        file_hash.update(data)
    # hex digest is better than digest, for standart use.
    return file_hash.hexdigest()

def load_saved_file_list(json_file_path):
    """
    loads the json file that has previously found files
    """
    external_file_list = {}
    try:
        with open(json_file_path, 'r') as json_data:
            external_file_list = json.load(json_data)
    except FileNotFoundError as e:
        print(f"Warning: {e.strerror}")
        print(f"warning: Missing {json_file_path}")
        print("Info: This is normal, if this is a first run of the program.")
    return external_file_list



# MAIN FUNCTION
def main():
    # Set properties
    min_file_size = 0
    volume_name = input(
        "Name the volume you're searching" +
        "(something distinct from other volumes): ")
    data_dir = "logs"
    outfile_suffix = "_filefish_out.log"
    load_external=True
    json_file_path='logs/json_data.json'
    json_stats_path='logs/json_stats.json'

    # ignore directories
    ignore = ['Volumes', '.Trash', '.MobileBackups', 'atest', 'Applications',
              '.git',
              '.gitignore',
              '.docker',
              '.local',
              '.config',
              '.dropbox',
              #   'Dropbox',
              'Downloads',
              'Windows',
              'drivers',
              'Program Files',
              'Program Files(x86)',
              'lib',
              'bin',
              'snap',
              'lost+found',
              'root',
              'sbin',
              'run',
              'sys',
              'tmp',
              'lib64',
              'proc',
              'dev',
              'local_dev',
              ]

    if os.name == 'nt':
        folder = input("Enter the drive letter you'd like to search: ")

        if folder == '':
            folder = "C:\\"
        else:
            folder = folder + ":\\"

    elif os.name == 'posix':
        print('OS is Mac/Linux')
        folder = input("Enter the file path (Default is './test/': ")
        if folder == '':
            folder = "./test/"

    else:  # quit if not NT OR POSIX
        exit()

    print (f"All files ending with .txt in folder {folder}:")
    file_list = {} if not load_external else load_saved_file_list(json_file_path)

    file_types = get_file_types_from_user()

    print(f"Start Time: {str(datetime.datetime.now().time())}")
    for (paths, dirs, files) in os.walk(folder, topdown=True):
        for ignore_dir in ignore:
            if ignore_dir in dirs:
                dirs.remove(ignore_dir)

        dirs[:] = [d for d in dirs if d not in ignore]
        # Testing section end...
        for file_to_check in files:
            # TODO: change this to check first if the file is the right size,
            #       do the checks.  Also use a "fancy" tuple with named values
            #       to store the min size per type instead of a global type
            for file_type in file_types.ft_list:
                temp_outfile = file_type.extension + outfile_suffix
                temp_outfile = os.path.join(data_dir, temp_outfile)
                if not os.path.exists(temp_outfile):
                    startFile = open(temp_outfile, 'w+')
                    startFile.write(
                            "Filename\t"
                            "Hash\t"
                            "FileSize\t"
                            "Date\t"
                            "FileType\t"
                            "VolumeName\n")
                    startFile.close()
                if (file_to_check.lower()).endswith(file_type.extension):
                    filename = os.path.join(paths, file_to_check)
                    with open(filename, 'rb') as file_to_hash:
                        file_hash = get_md5(file_to_hash)
                        file_stat = os.stat(filename)
                        timestamp = str(modification_date(filename))
                        file_size = str(file_stat.st_size)
                        path_tags = [tag for tag in filter(None,filename.split("/"))]
                        if int(file_type.min_size) < int(file_size):
                            if file_hash not in file_list.keys():
                                file_list[file_hash] = []
                            file_list[file_hash].append({
                                    'tags': path_tags,
                                    'filename': str(path_tags[-1]),
                                    'md5hash': file_hash,
                                    'full_path': filename,
                                    'volume': volume_name,
                                    'file_size': file_size,
                                    'timestamp': timestamp,
                                    })
                            # if file_stat.st_size > min_file_size:
                            with open(temp_outfile, 'a+') as out_put_file:
                                out_put_file.writelines(
                                    "{}\t{}\t{}\t{}\t{}\t{}\t{}\t\n".format(
                                        str(path_tags[-1]),
                                        filename,
                                        file_hash,
                                        file_size,
                                        timestamp,
                                        file_type,
                                        volume_name,

                                            )
                            )

    # debug
    # print([
    #     """\nhash: {}
    #     count: {}
    #     fileslist:
    #     __________
    #     {}""".format(i, len(file_list[i]), file_list[i]) for i in file_list])
    print(f"End Time: {str(datetime.datetime.now().time())}")
    print(f"All done.... See {data_dir} folder for output files")
    print(f"All done.... See {json_file_path} folder"
            "accumlated json from all sources")
    
    stats = {}
    for key in file_list:
        stats[key] = stats.pop(key, None)
        if stats[key] is None:
            stats[key] = {}
        stats[key]['files'] = file_list[key]
        stats[key]['copies'] = len(file_list[key])
        stats[key]['md5'] = key
    
    # pprint(stats)

    """re-save the data to a file
    """

    with codecs.open(
            json_file_path, 'w+', encoding='utf-8'
            ) as json_out:
        json_out.write(
                json.dumps(file_list, sort_keys=True, ensure_ascii=False))

    """dump out the stats to a file
    """

    with codecs.open(
            json_stats_path, 'w+', encoding='utf-8'
            ) as json_out:
        json_out.write(
                json.dumps(stats, sort_keys=True, ensure_ascii=False))

    mulitple_files_collection = [
            stats[dups] for dups in stats if stats[dups]['copies'] > 1
        ]

    with codecs.open(
            json_stats_path, 'a+', encoding='utf-8'
            ) as json_out:
        json_out.writelines("\n \\\\***MORE THAN ONE***\n")
        json_out.write(
                json.dumps(mulitple_files_collection[0], sort_keys=True, ensure_ascii=False))    

if __name__ == '__main__':
    main()
