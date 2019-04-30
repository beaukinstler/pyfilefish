from dotenv import load_dotenv
from os import getenv
import logging

load_dotenv()

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig( filename='./logs/app_log.txt', level=logging.INFO,
        format=LOG_FORMAT)
logger = logging.getLogger()

# set whether the app attempts to import previously stored json data from the JSON_FILE_PATH
LOAD_EXTERNAL=True
SYNC_TO_LOCAL=False
SYNC_TO_S3=False
ALL_SIZES=False
WRITE_OUT_DATA=False
WRITE_OUT_STATS=False
WRITE_OUT_MULTI=False

# local file paths from .env settings
JSON_FILE_PATH = getenv('JSON_FILE_PATH')
JSON_FILE_PATH_TEMP = getenv('JSON_FILE_PATH_TEMP')
JSON_STATS_PATH = getenv('JSON_STATS_PATH')
JSON_MULTI_SUMMARY_FILE = getenv('JSON_MULTI_SUMMARY_FILE')
FLAT_FILE_DATA_DIR = getenv('FLAT_FILE_DATA_DIR')
FLAT_FILE_SUFFIX = getenv('FLAT_FILE_SUFFIX')



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