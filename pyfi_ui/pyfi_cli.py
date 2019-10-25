import os
from filetypes import FilePropertySet
from settings import VOLUME_TYPES
from pyfi_util.pyfish_util import (
    get_current_volumes,
    get_unique_files_totalsize,
)
from pathlib import Path


def prompt_for_local_dest():
    prompt = """
        Enter a file path where Pyfish can find you local 
        storeage.  Make sure the path will not be scanned.
        Enter the full path: 
        """
    dest = input(prompt)
    return dest


def prompt_windows_folder(drive_ui: str = "", folder_ui: str = ""):
    print("Enter a drive leter and sub folder that you'd like to search.\n")
    print('ie. "C:\\"')
    konch = False
    drive = Path(drive_ui + ":/")
    folder = ""
    while konch == False:
        if not drive_ui:
            drive = input("Enter the drive letter you'd like to search: ")
            drive = Path(str(drive) + ":/")
        else:
            konch = True
        try:
            if drive.exists():
                konch = True
            else:
                print(
                    "That drive isn't mounted.  Please choose a drive that is available"
                )
        except OSError:
            print(
                "That file system doens't seem to be valid. \
                        Please ensure you can access the file system. Perhaps remount the drive if not."
            )
            if drive_ui:
                raise ValueError

    konch = False
    temp_folder = ""
    while konch == False:
        if drive_ui:
            folder = drive.joinpath(folder_ui)
            break
        else:
            temp_folder = input(
                'Please enter a subfolder (i.e "Users/sue"),\n \
                            or just press [Enter] to use the whole drive: '
            )
            folder = drive.joinpath(temp_folder)

        if folder.exists():
            konch = True
        else:
            print("\nSorry, that is not a valid path.  Please try again.")

    return str(folder)


def prompt_folder_to_scan():

    # if os.name == 'nt':
    #     folder = prompt_windows_folder()

    # elif os.name == 'posix':

    if os.name in ["posix", "nt"]:
        print("OS is Mac/Linux or Windows NT")
        folder = input(
            "Enter the file path (Default is './tests/test_files': "
        )
        if folder == "":
            folder = "./tests/test_files"

    else:
        folder = None

    return folder


def get_file_types_from_user():
    """prompt user for file types and return a FilePropertySet()
    """
    # fileTypeList = ['png', 'jpeg', 'mp4', 'bmp', 'wav', 'jpg', ]
    filePropList = FilePropertySet()
    file_type_input = ""
    while True:
        if file_type_input == "new":
            # fileTypeList = []
            filePropList.clear()
        # fileTypeList.append(file_type_input)
        prompt_text = (
            "Please input file types to search for, but don't "
            + "add the period.\n  Or just press enter or type 'done' if satisfied with...\n"
            + ", ".join([prop.extension for prop in filePropList.ft_list])
            + "\n: "
        )
        prompt_text += "Or type 'new' to clear the list and start over\n"
        file_type_input = input(prompt_text)
        if file_type_input in ["done", ""]:
            break
        if file_type_input != "new":
            print(
                "Please enter a mininimum size in bytes."
                "(smaller files will be ignored.)"
            )
            min_size = input("mininmum size: ")
            filePropList.add(
                filePropList.file_properties(file_type_input, min_size)
            )

    # return fileTypeList
    return filePropList


def _select_volume_from_list(previous_volumes: list, existing_only=False):
    """present a list of volumes to choose from and over to enter a new one
    
    Arguments:
        previous_volumes {list} -- a list of volume names found in the saved 
        data
    
    Returns:
        str -- either a new volume name, or one from the list
    """

    select_list = [
        (key, previous_volumes[key - 1])
        for key in range(1, len(previous_volumes) + 1)
    ]
    result = ""
    confirm = "n"
    new_volume_prompt = "HINT: Names should be unique, and help you know where the volume is.\n"
    new_volume_prompt += "i.e: 'Macbook Lucy/ HD01'\n"
    new_volume_prompt += (
        "Please enter a new name, but it should not match an existing name: "
    )
    # we'll loop the prompt until the user is sure of their selection
    entry = 0
    while confirm[0].lower() != "y":
        if previous_volumes:
            print("You can choose a volume/location found in the saved data\n")
            for key, volume in select_list:
                print(f"press '{key}' for '{volume}'")
            if not existing_only:
                entry = input(
                    "Type the number, or '0' to add a new volume and press Enter': "
                )
            else:
                entry = input(
                    "Type the number computer volume and press 'Enter': "
                )
        try:
            entry = int(entry)
        except:
            if not entry:
                entry = 0
        entry = str(input(new_volume_prompt)) if str(entry) == "0" else entry
        prompt_entry = (
            entry if type(entry) is str else previous_volumes[entry - 1]
        )
        confirm = (
            input(
                f"\nYou entered '{prompt_entry}'. Is that correct? (yes,no,cancel): "
            )
            if entry
            else "n"
        )
        confirm = "y" if confirm == "" else confirm
        if confirm[0].lower() == "c":
            print("You have canceled. Existing")
            exit()
        # get the text name if a previous volume slected.
        if type(entry) == int:
            result = previous_volumes[entry - 1]
        else:
            result = entry
            if result in previous_volumes:
                print("SORRY, you can't use a name that's been used already\n")
                confirm = "n"
                result = ""
        # reset confirm if blank
        if not confirm:
            confirm = "n"

    # return the volume name to use
    return str(result)


def prompt_for_volume(existing_only=False):
    previous_volumes = [vol for vol in get_current_volumes()]
    volume = _select_volume_from_list(previous_volumes, existing_only)
    if not existing_only:
        volume_name = (
            input(
                "Name the volume you're searching"
                + "(something distinct from other volumes): "
            )
            if not volume
            else volume
        )
    else:
        volume_name = volume
    return volume_name


       



def prompt_volume_type():
    """ prompt user for type of volume
    
    Returns:
        tuple(int,str) -- Number chosen and  description
    """
    option_list = [ vt.description for vt in VOLUME_TYPES ]

    print_numbered_options(option_list)
    
    choice = 0
    while choice not in range(1,len(option_list)):
        try:
            choice = int(input("Make choice from a number in the list above: "))        
        except ValueError as e:
            print("Please enter a number.\nPlease try again.\n")
        # print("That entry wasn't something we can work with.\nPlease try again.\n")
    return (choice, VOLUME_TYPES[ choice - 1 ])

def prompt_user_for_size_one_volume():
    print("Please choose a volume name to search for size")
    vol = prompt_for_volume(existing_only=True)
    size = get_unique_files_totalsize(None, vol)
    print(f"\nVolume: {vol}\n")
    print(f"Size  : {size}\n")

def get_options_list():
    return(
        """
        1)  see unique file size totals. This roughly show the amount of disk space required to store all the files in the data
        2)  see the volumes currentinly captured in the data
        3)  Scan and find files, as well as sync to AWS S3 bucket.
             (Note: you must already have your cli and bucket configured for this to work)
        4)  Scan and find files, and simultaneously copy them to a local target.
        5)  Sync previously scanned files to local target
        6)  Get the size of one volume, based on data previously captured.
        7)  TODO: Print Stats after scanning.
        11) EXIT
        0) Scan and find files for data, but do not sync to another location
        """
    )

def prompt_user_for_run_mode():
    """sub routine to report on previous data
    """
    print(get_options_list())
    prompt = "Select an option. Choose 0 to just run the scanner, creating a list of files to act on later: "
    
    try:
        choice = int(input(prompt))
        print("\n")
    except Exception as e:
        print(f"'not a valid choice': {e}")
        choice = 0

    if choice:
        if choice == 1:
            print(
                f"Total size of files stored in MB: {get_unique_files_totalsize()}"
            )
        elif choice == 2:
            print([i for i in get_current_volumes()])
        elif choice == 4:
            print("local destination needed")
        elif choice == 5:
            print("local destination needed")
        elif choice == 6:
            print("Getting Volume name...\n\n")
            prompt_user_for_size_one_volume()
        elif choice > 6:
            choice = 999
        return choice
    else:
        return choice



def print_numbered_options(list_of_options:list, indent=" "*4, sep=")  "):
    """prints out a list with numbers to choose
    
    Arguments:
        list_of_options {list} -- [description]
    """
    for count, item in enumerate(list_of_options, start=1):
        print(f"{indent}{count}{sep}{item}")

    
