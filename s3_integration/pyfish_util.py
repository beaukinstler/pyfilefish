from pyfi import load_saved_file_list
from pyfi import JSON_FILE_PATH


def load_pyfish_data():
    file_list = load_saved_file_list(JSON_FILE_PATH)
    return file_list


def get_unique_files_totalsize(filelist=None):
    """return the sum of MB stored in a pyfish file list
    
    Arguments:
        filelist {dict} -- file_list as created by pyfish.
        may also be loaded form a json_data.json that is 
        created and loaded by pyfish
    
    Returns:
        float -- sum of only the first instace for each unique
        file.
    """

    if not filelist:
        filelist = load_pyfish_data()

    return sum([ float(filelist[i][0]['file_size']) for i in filelist ])