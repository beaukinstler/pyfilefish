from dotenv import load_dotenv
from os import getenv
import os
import logging

load_dotenv()
# set whether the app attempts to import previously stored json data from the JSON_FILE_PATH
LOAD_EXTERNAL=True
SYNC_TO_LOCAL=False
SYNC_TO_S3=False
ALL_SIZES=True
WRITE_OUT_DATA=True
WRITE_OUT_STATS=True
WRITE_OUT_MULTI=True
WRITE_OUT_FLAT=True

# local file paths from .env 
DATA_FOLDER = getenv('DATA_FOLDER')
LOG_FOLDER = getenv("LOG_FOLDER")
JSON_FILE_PATH = os.path.join(DATA_FOLDER, getenv('JSON_FILE_PATH'))
JSON_FILE_PATH_TEMP = os.path.join(DATA_FOLDER, getenv('JSON_FILE_PATH_TEMP'))
JSON_STATS_PATH = os.path.join(DATA_FOLDER,getenv('JSON_STATS_PATH'))
JSON_MULTI_SUMMARY_FILE = os.path.join(DATA_FOLDER, getenv('JSON_MULTI_SUMMARY_FILE'))
FLAT_FILE_DATA_DIR = getenv('FLAT_FILE_DATA_DIR')
FLAT_FILE_SUFFIX = getenv('FLAT_FILE_SUFFIX')

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(FLAT_FILE_DATA_DIR, exist_ok=True)
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
LOG_FILE_NAME = os.path.join(LOG_FOLDER, 'app_log.txt')
logging.basicConfig(filename=LOG_FILE_NAME, level=logging.INFO,
        format=LOG_FORMAT)
logger = logging.getLogger()

# ignore directories
IGNORE_DIRS = ['Volumes', '.Trash', '.MobileBackups', 'atest', 'Applications',
            'Library', 'System', 'User Information', 'usr', 
            'opt', 'var',
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
            'dotfiles',
            'test_skip_dir'
            ]