from flask import Flask, request, redirect, send_from_directory, render_template
from pathlib import Path
from flask_socketio import SocketIO, emit
import os
import urllib
import time
import threading
from src import vlc, drive, computer
from urllib.parse import unquote
from datetime import datetime
from termcolor import colored


app = Flask(__name__, template_folder="../static")
socketio = SocketIO(app, cors_allowed_origins='*')

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
    os.system('taskkill /f /im msedge.exe >nul 2>&1')
    with _lstatus:
        _status = "play"


def autoplay(time=5*60.0):
    global _timeout
    if _timeout != None:
        _timeout.cancel()
    _timeout = threading.Timer(time, _autoplay)
    _timeout.start()


def status():
    global _status, _lstatus
    if drive.find() != None:
        return 'usb'
    with _lstatus:
        return _status


def addr():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For")
    else:
        return request.remote_addr


@socketio.on('connect')
def on_connect():
    if addr() != "127.0.0.1" and request.cookies.get('secret') != app.secret:
        return False


@socketio.on('projector-ready')
def projector_ready(id):
    emit('projector-ready', id, broadcast=True)


@socketio.on('projector-keep')
def projector_keep():
    autoplay(time=15.0)


@socketio.on('cast')
def cast():
    global _status, _lstatus
    with _lstatus:
        _status = "pause"
    emit('projector-stop', broadcast=True, include_self=False)
    vlc.stop()
    autoplay(time=15.0)
    os.system('taskkill /f /im msedge.exe >nul 2>&1')
    os.system('start /b "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk http://localhost:5000/projector --edge-kiosk-type=fullscreen')
    return 200


@app.before_request
def before_request_func():
    now = datetime.now()
    log = colored(now.strftime("%H:%M:%S"), 'blue') + " → " + request.path
    print(log)


@app.route('/login')
def login():
    if request.cookies.get('secret') == app.secret:
        return redirect('/')
    return render_template('login.html', name=computer.name())


@app.route('/projector')
def projector():
    if addr() != '127.0.0.1':
        return redirect('/')
    return render_template('projector.html')


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

        if vlc.check():
            vlc.stop()
            time.sleep(1)
            autoplay()

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

        if vlc.check():
            vlc.stop()
            time.sleep(1)
            autoplay()

        file.save(path)
        return redirect('/?upload')

    return "400 (Bad Request)", 400


def run():
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socketio.run(app, host='0.0.0.0', port=5000)


def start(secret):
    app.secret = secret
    daemon = threading.Thread(target=run, daemon=True)
    daemon.setDaemon(True)
    daemon.start()
