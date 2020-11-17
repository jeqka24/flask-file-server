from functools import wraps
from uuid import uuid4
import os

from threading import Timer
import webbrowser

import flask
from flask import request, Flask, abort, render_template, redirect, url_for

from entities import db, File, FileState, User

from utils import encode, decode

UPLOAD_DIR = "upload"

CUR_DIR = os.path.realpath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(CUR_DIR, UPLOAD_DIR)

APIKEY_NAME = 'api-key'
# DEBUG = True

app = Flask(
    __name__,
    static_folder=os.path.join(CUR_DIR, 'static'),

    #    template_folder=os.path.join(CUR_DIR, 'templates')
    template_folder=os.path.join(CUR_DIR, 'templates')

    )

app.config.from_object(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


def get_request_data():
    if request.method == 'POST':
        return request.form
    return request.args


def get_user():
    request_data = get_request_data()
    auth_token = request.headers.get(APIKEY_NAME, None) or request_data.get(APIKEY_NAME, None)
    user = User.get_or_none(auth_token=auth_token)
    return user


def get_file_path(file):
    return os.path.join(os.path.curdir, UPLOAD_DIR, file)


def require_auth(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        us = get_user()
        if not (us):
            abort(403, "Wrong Auth")
        return fn(*args, **kwargs)

    return inner


def require_file(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        file = request.files.get("files", None)

        if not (os.path.exists(os.path.abspath(get_file_path(file)))):
            abort(404)

        if file not in db.File:
            abort(404)
        return fn(file, *args, **kwargs)

    return inner


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([File, FileState, User])
    FileState.create(state="Загружается", r_accessible=False)
    FileState.create(state="Загружен")
    FileState.create(state="Кодируется", r_accessible=False)
    FileState.create(state="Закодирован")
    FileState.create(state="Удален", r_accessible=False, d_accessible=False)
    u = User.create(auth_token=uuid4(), pkey=generate_key())
    app.logger.info("First user: %s" % u.auth_token)
    db.commit()


@app.route('/upload', methods=['POST'])
@require_auth
def upload():
    app.logger.info("New upload request")
    # 2. chek file in upload
    if request.method == 'POST' and 'files' in request.files:
        f = request.files['files']  # f is werkzeug.datastructures.FileStorage
        filename = str(uuid4())
        owner = get_user()

        app.logger.info("store original name and uuid in File")

        state = FileState.get_or_none(state="Загружается")
        curr_file = File.create(uuid=filename, name=f.filename, state=state.id, owner=owner)
        app.logger.info("save to FS")
        f.save(dst=os.path.join(app.config['UPLOAD_FOLDER'], filename))

        state = FileState.get_or_none(state="Загружен")
        curr_file.state = state.id
        curr_file.save()

        # create a task of encrypting file
        state = FileState.get_or_none(state="Кодируется")
        curr_file.state = state.id
        curr_file.save()
        # encode - still empty

        state = FileState.get_or_none(state="Закодирован")
        curr_file.state = state.id
        curr_file.save()


    app.logger.info("Upload request finished")
    return redirect(url_for('home', **{APIKEY_NAME: owner.auth_token}))


@app.route('/download/<file>')
@require_auth
def download(file, **kwargs):
    # 1. Check request for api-key
    us = get_user()
    if not (us):
        abort(401)

    # 2. Check file & api-key existance in File
    fob = File.get_or_none(uuid=file, owner=us)

    # 3. Check file state in FileState: should be r_accessible
    if fob:
        fs = FileState.get_or_none(fob.state)  # file state
    else:
        abort(404)
    if fs.r_accessible:
        return flask.send_file(filename_or_fp=get_file_path(file), as_attachment=True, attachment_filename=fob.name)
    else:
        abort(403)


@app.route("/delete/<file>")
@require_auth
def delete(file):
    us = get_user()
    Query = File.delete().where(File.uuid == file)
    Query.execute()
    os.remove(get_file_path(file))
    return redirect(url_for("home",  **{APIKEY_NAME:us.auth_token}), code=302)


@app.route("/", methods=["GET", ])
def index():
    us = get_user()
    if not(us):
        abort(401, "API key required")
    return redirect(url_for("home",  **{APIKEY_NAME:us.auth_token}), code=302)


@app.route('/home', methods=["GET", ])
@require_auth
def home():
    us = get_user()
    if not (us):
        abort(401, "API key required")
    files = File.select().where(File.owner == us)
    return render_template("home.html", APIKEY_NAME=APIKEY_NAME, files=files, user=us.auth_token)


@app.route('/mirror', methods=["GET", "POST"])
def mirror(**kvargs):
    kvargs['a'] = request.headers
    kvargs['b'] = get_request_data()
    kvargs['c'] = request.files
    return render_template("mirror.html", **kvargs)

def browser():
    webbrowser.open_new("http://127.0.0.1:8090/home?%s=%s" % (APIKEY_NAME, User[1].auth_token))

# application execution
if __name__ == '__main__':
    if not (db.database):
        init_db()
    Timer(1.25, browser()).start()
    app.run(port=8090)
