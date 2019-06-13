from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask import send_from_directory
from pathlib import Path
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from pyfi_util import pyfish_util as pfu

bp = Blueprint('pyfi', __name__)


@bp.route('/pyfi')
def pyfi():
    """Show all the posts, most recent first."""
    # file_set = pfu.load_....
    file_set = pfu.load_pyfish_data()
    posts = []

    for md5 in file_set:
        for file_list in file_set[md5]:
            posts.append({
                        'filename': file_list['filename'],
                        'full_path': file_list['full_path'],
                        'timestamp': file_list['timestamp'],
                        'volume': file_list['volume'],
                        'filetype': file_list['filetype'],
                        'md5hash': file_list['md5hash']})
    return render_template('pyfi/index.html', posts=posts)


@bp.route('/pyfi/<vol>/<md5hash>')
def send_file(vol, md5hash):
    # test = [
    #             {
    #                 "file_size": "1.0",
    #                 "filename": "test.jpg",
    #                 "filetype": "mp3",
    #                 "full_path": "C:\\Users\\Beau\\local_dev\\pyfilefish\\tests\\test_files\\test.jpg",
    #                 "inode": "9007199254825275",
    #                 "md5hash": "b6d81b360a5672d80c27430f39153e2c",
    #                 "tags": [
    #                     "c:\\",
    #                     "users",
    #                     "beau",
    #                     "local_dev",
    #                     "pyfilefish",
    #                     "tests",
    #                     "test_files",
    #                     "test.jpg"
    #                 ],
    #                 "timestamp": "2019-05-03 14:24:08.735000",
    #                 "volume": "xps"
    #             },]

    file_record = pfu.load_pyfish_data(md5hash)
    # import pdb; pdb.set_trace()
    fullpath = [i['full_path'] for i in file_record if i['volume'] == vol][0]
    realdir = str(Path(fullpath).parent)
    name = str(Path(fullpath).name)
    print(realdir)
    print(name)
    return send_from_directory(realdir, name)