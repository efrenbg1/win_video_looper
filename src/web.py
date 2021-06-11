from flask import Flask, request, redirect, send_from_directory, render_template
from pathlib import Path
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import urllib
import time
import threading
from src import vlc, drive, computer
from urllib.parse import unquote


app = Flask(__name__, template_folder="../static")
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["20 per minute"]
)

storage = os.path.realpath(os.path.join(Path(__file__).parent, '../storage'))
if not os.path.exists(storage):
    os.makedirs(storage)
storage1 = os.path.realpath(os.path.join(Path(__file__).parent, '../storage/files'))
if not os.path.exists(storage1):
    os.makedirs(storage1)
storage2 = os.path.realpath(os.path.join(Path(__file__).parent, '../storage/featured'))
if not os.path.exists(storage2):
    os.makedirs(storage2)

_status = "play"
_lstatus = threading.Lock()
_timeout = None


def _autoplay():
    global _status, _lstatus
    with _lstatus:
        _status = "play"


def autoplay():
    global _timeout
    if _timeout != None:
        _timeout.cancel()
    if app.autoplay:
        _timeout = threading.Timer(5*60.0, _autoplay)
        _timeout.start()


def status():
    global _status, _lstatus
    if drive.find() != None:
        return 'usb'
    with _lstatus:
        return _status


@app.route('/login')
def login():
    if request.cookies.get('secret') == app.secret:
        return redirect('/')
    return render_template('login.html', name=computer.name())


@app.route("/")
def root():
    if request.cookies.get('secret') != app.secret:
        return redirect('/login')
    files = []
    featured = []
    for f in os.listdir(storage1):
        date = os.path.getmtime(os.path.join(storage1, f))
        date = time.localtime(date)
        date = time.strftime('%d/%m/%Y %H:%M ', date)
        files.append({
            'url': f,
            'filename': unquote(f),
            'date': date
        })
    for f in os.listdir(storage2):
        date = os.path.getmtime(os.path.join(storage2, f))
        date = time.localtime(date)
        date = time.strftime('%d/%m/%Y %H:%M ', date)
        featured.append({
            'url': f,
            'filename': unquote(f),
            'date': date
        })
    return render_template('index.html', name=computer.name(), featured=featured, files=files, status=status())


@app.route("/playpause")
def playpause():
    global _status, _lstatus
    if request.cookies.get('secret') != app.secret:
        return redirect('/login')
    if status() == 'usb':
        return redirect('/?usb')
    with _lstatus:
        if _status == "play":
            _status = "pause"
        else:
            _status = "play"
    vlc.stop()
    autoplay()
    return redirect('/')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../static/', path)


@app.route('/storage/<folder>/<action>/<file>')
@app.route('/storage/<folder>/<action>', methods=["POST"])
def api(folder, action, file=""):
    if request.cookies.get('secret') != app.secret:
        return redirect('/login')

    file = urllib.parse.quote(file)
    if folder == "featured":
        folder = storage2
    else:
        folder = storage1

    if action == "watch" and request.method == "GET":
        return send_from_directory(folder, file)

    elif action == "download" and request.method == "GET":
        return send_from_directory(folder, file, as_attachment=True)

    elif action == "delete" and request.method == "GET":
        global _lstatus
        autoplay()

        if file not in os.listdir(folder):
            return redirect('/?path')

        path = os.path.join(folder, file)
        if os.path.commonprefix((os.path.realpath(path), folder)) != folder:
            return redirect('/?path')

        if status() == "play":
            return redirect('/?status')

        os.remove(path)
        return redirect('/?delete')

    elif action == "upload" and request.method == "POST":
        autoplay()

        file = request.files.get('file')
        if file is None:
            return redirect('/?file')

        filename = urllib.parse.quote(file.filename)
        if filename in os.listdir(folder):
            return redirect('/?exists')

        path = os.path.join(folder, filename)
        if os.path.commonprefix((os.path.realpath(path), folder)) != folder:
            return redirect('/?path')

        if status() == "play":
            return redirect('/?status')

        file.save(path)
        return redirect('/?upload')

    return "400 (Bad Request)", 400


def run():
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=8080)


def start(secret, autoplay):
    app.secret = secret
    app.autoplay = autoplay
    daemon = threading.Thread(target=run, daemon=True)
    daemon.setDaemon(True)
    daemon.start()
