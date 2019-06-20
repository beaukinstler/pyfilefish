from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask import send_from_directory
from pathlib import Path
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from pyfi_util import pyfish_util as pfu
from settings import APPMODE

bp = Blueprint('pyfi', __name__)


@bp.route('/pyfi')
@login_required
def pyfi():
    """Show all the posts, most recent first."""
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


@bp.route('/pyfi/<vol>/<md5hash>.<extension>')
@login_required
def send_file(vol, md5hash, extension):
    file_record = pfu.load_pyfish_data(md5hash)
    fullpath = Path( [i['full_path'] for i in file_record if i['volume'] == vol][0] ).absolute()
    realdir = str(Path(fullpath).parent)
    name = str(Path(fullpath).name)
    return send_from_directory(realdir, name, as_attachment=False)