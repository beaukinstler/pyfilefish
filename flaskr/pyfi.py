from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from flask import send_from_directory
from pathlib import Path
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from pyfi_util import pyfish_util as pfu
from settings import APPMODE
from flask_paginate import Pagination, get_page_parameter

bp = Blueprint("pyfi", __name__)

@bp.route("/volumes")
@login_required
def volumes():
    return render_template("pyfi/volumes.html", volumes=pfu.get_current_volumes())

@bp.route("/pyfi")
@login_required
def pyfi():
    """Show all the posts, most recent first."""
    file_set = pfu.load_pyfish_data()
    posts = []

    # for pagination
    search = False
    filetype,volume = request.args.get('filetype'),request.args.get('volume')
    if filetype:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    for md5 in file_set:
        for file_list in file_set[md5]:
            if (not filetype or str(file_list["filetype"]).lower() == str(filetype).lower()) \
                and (not volume or str(file_list["volume"]).lower() == str(volume).lower()):
                posts.append(
                    {
                        "filename": file_list["filename"],
                        "full_path": file_list["full_path"],
                        "timestamp": file_list["timestamp"],
                        "volume": file_list["volume"],
                        "filetype": file_list["filetype"],
                        "md5hash": file_list["md5hash"],
                        "file_size": file_list["file_size"],
                    }
                )
    
    pagination = Pagination(
            page=page,
            total=len(posts),
            search=search,
            record_name='Posts',
            found= len(posts),
        )

    posts2 = posts[pagination.skip:pagination.total-1] \
            if page == pagination.total_pages \
            else posts[pagination.skip:pagination.skip+pagination.per_page]

    # if str(filetype).lower() == 'mp3':
    #     posts2 = [ post for post in posts2 if post['filetype'].lower() == 'png']
    #     pagination.found = len(posts2)

    return render_template("pyfi/index.html", Posts=posts2, pagination=pagination)


@bp.route("/pyfi/<vol>/<md5hash>.<extension>")
@login_required
def send_file(vol, md5hash, extension):
    file_record = pfu.load_pyfish_data(md5hash)
    fullpath = Path( [i['full_path'] for i in file_record if i['volume'] == vol][0] ).absolute()
    realdir = str(Path(fullpath).parent)
    name = str(Path(fullpath).name)
    return send_from_directory(realdir, name, as_attachment=False)
