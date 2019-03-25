

# Purpose: get all files ending with a given extension in a drive or folder

import os
from hashlib import md5
import datetime
import json
import codecs


# Functions to move to another module or class
def get_file_types_from_user():
    """prompt user for file types and return a list
    """
    fileTypeList = ['png', 'jpeg', 'mp4', 'bmp', 'wav', 'jpg', ]
    file_type_input = 'mp3'  # default
    while file_type_input != "0":
        if file_type_input == 'new':
            fileTypeList = []
        fileTypeList.append(file_type_input)
        prompt_text = "Please input file types to search for, but don't " + \
            "add the period.\n  Enter '0' if satisfied with - " + \
            ','.join(fileTypeList) + "\n: "
        prompt_text += "Or type 'new' to clear the list and start over\n"
        file_type_input = raw_input(prompt_text)
    return fileTypeList


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


# MAIN FUNCTION
def main():
    # Set properties
    min_file_size = 0
    volume_name = raw_input(
        "Name the volume you're searching" +
        "(something distinct from other volumes): ")
    data_dir = "logs"
    outfile_suffix = "_filefish_out.txt"

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
              ]

    if os.name == 'nt':
        folder = raw_input("Enter the drive letter you'd like to search: ")

        if folder == '':
            folder = "C:\\"
        else:
            folder = folder + ":\\"

    elif os.name == 'posix':
        print 'OS is Mac/Linux'
        folder = raw_input("Enter the file path (Default is './test/': ")
        if folder == '':
            folder = "./test/"

    else:  # quit if not NT OR POSIX
        exit()

    print "All files ending with .txt in folder %s:" % folder
    file_list = {}

    file_types = get_file_types_from_user()

    # create output files if they don't exist.
    # for file_type in file_types:
    #       # Make the outfile_suffix append with the file type.
    #       #   THis keeps the output file specific to file type.
    #       #   Strip out the '.' from the file type
    #   file_type_no_period = file_type.translate(None,'.')
    #   temp_outfile = file_type_no_period + outfile_suffix
    #   try: # check if the file exists already
    #       blank=open(temp_outfile,'r')
    #       blank.close()
    #       print "DEBUG: the file exists and can be opened."
    #   except IOError, e:
    #      # since the file doesn't exist, create the file and add the header
    #       print "DEBUG:  the file doesn't exists"
    #       startFile = open(temp_outfile,'a')
    #       startFile.write("Filename\tHash\tFileSize\tDate\tFileType\tVolumeName\n")
    #       startFile.close()

    # start the walking process.
    print "Start Time: " + str(datetime.datetime.now().time())
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
            for file_type in file_types:
                # file_type_no_period = file_type.translate(None,'.')
                temp_outfile = file_type + outfile_suffix
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
                if file_to_check.endswith(file_type):
                    with open(temp_outfile, 'a+') as out_put_file:
                        filename = os.path.join(paths, file_to_check)
                        with open(filename, 'rb') as file_to_hash:
                            file_hash = get_md5(file_to_hash)
                            file_stat = os.stat(filename)
                            if file_hash not in file_list.keys():
                                file_list[file_hash] = []
                            file_list[file_hash].append(
                                    {'md5hash': file_hash,
                                     'full_path': os.path.join(
                                            paths,
                                            file_to_check),
                                     })
                            if file_stat.st_size > min_file_size:
                                out_put_file.writelines(
                                    "{}\t{}\t{}\t{}\t{}\t{}\t\n".format(
                                        filename,
                                        file_hash,
                                        str(file_stat.st_size),
                                        str(modification_date(filename)),
                                        file_type,
                                        volume_name,

                                            )
                                )

    # debug
    print [
        """\nhash: {}
        count: {}
        fileslist:
        __________
        {}""".format(i, len(file_list[i]), file_list[i]) for i in file_list]
    print "All done.... See {} folder for output files".format(data_dir)
    print "End Time: " + str(datetime.datetime.now().time())

    with codecs.open(
            'logs/json_result.json', 'a+', encoding='utf-8'
            ) as json_out:
        json_out.write(
                json.dumps(file_list, sort_keys=True, ensure_ascii=False))


if __name__ == '__main__':
    main()
