from flask import Flask, request, redirect, send_from_directory, render_template
from flask_socketio import SocketIO, emit
import os
import urllib
import time
import threading
from src import computer, browser, storage, worker
import settings
from urllib.parse import unquote
from datetime import datetime
from termcolor import colored


app = Flask(__name__, template_folder="../static")
socketio = SocketIO(app, cors_allowed_origins='*')


_casting = None
_lcasting = threading.Lock()


def casting():
    global _casting, _lcasting
    with _lcasting:
        if _casting != None:
            return True
    return


def addr():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(',')[0]
    else:
        return request.remote_addr


@socketio.on('connect')
def on_connect():
    if addr() != '127.0.0.1' and request.cookies.get('secret') != settings.secret:
        return False


@socketio.on('disconnect')
def on_disconnect():
    global _casting, _lcasting
    with _lcasting:
        if _casting == request.sid:
            _casting = None


@socketio.on('projector-ready')
def projector_ready(id):
    emit('projector-ready', id, broadcast=True)


@socketio.on('cast')
def cast():
    global _lstatus, _status, _lcasting, _casting
    worker.pause()
    with _lcasting:
        _casting = request.sid
    emit('projector-stop', broadcast=True, include_self=False)
    browser.start()
    return 200


@app.before_request
def before_request_func():
    now = datetime.now()
    log = colored(now.strftime("%H:%M:%S"), 'blue') + " → " + request.path
    print(log)


@app.route('/login')
def login():
    if request.cookies.get('secret') == settings.secret:
        return redirect('/')
    return render_template('login.html', name=computer.name())


@app.route('/projector')
def projector():
    if addr() != '127.0.0.1':
        return redirect('/')
    return render_template('projector.html')


@app.route("/")
def root():
    if request.cookies.get('secret') != settings.secret:
        return redirect('/login')
    files = []
    featured = []
    for f in os.listdir(storage.files):
        date = os.path.getmtime(os.path.join(storage.files, f))
        date = time.localtime(date)
        date = time.strftime('%d/%m/%Y %H:%M ', date)
        files.append({
            'url': f,
            'filename': unquote(f),
            'date': date
        })
    for f in os.listdir(storage.featured):
        date = os.path.getmtime(os.path.join(storage.featured, f))
        date = time.localtime(date)
        date = time.strftime('%d/%m/%Y %H:%M ', date)
        featured.append({
            'url': f,
            'filename': unquote(f),
            'date': date
        })
    return render_template('index.html', name=computer.name(), featured=featured, files=files)


@app.route('/403')
def outsider():
    return render_template('outsider.html', name=computer.name())


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../static/', path)


@app.route('/storage/<folder>/<action>/<file>')
@app.route('/storage/<folder>/<action>', methods=["POST"])
def api(folder, action, file=""):

    if request.cookies.get('secret') != settings.secret:
        return redirect('/login')

    file = urllib.parse.quote(file)
    if folder == "featured":
        folder = storage.featured
    else:
        folder = storage.files

    if action == "watch" and request.method == "GET":
        return send_from_directory(folder, file)

    elif action == "download" and request.method == "GET":
        return send_from_directory(folder, file, as_attachment=True)

    elif action == "delete" and request.method == "GET":
        if file not in os.listdir(folder):
            return redirect('/?path')

        path = os.path.join(folder, file)
        if os.path.commonprefix((os.path.realpath(path), folder)) != folder:
            return redirect('/?path')

        worker.pause()
        time.sleep(1)

        os.remove(path)
        return redirect('/?delete')

    elif action == "upload" and request.method == "POST":
        file = request.files.get('file')
        if file is None:
            return redirect('/?file')

        filename = urllib.parse.quote(file.filename)
        if filename in os.listdir(folder):
            return redirect('/?exists')

        path = os.path.join(folder, filename)
        if os.path.commonprefix((os.path.realpath(path), folder)) != folder:
            return redirect('/?path')

        worker.pause()
        time.sleep(1)

        file.save(path)
        return redirect('/?upload')

    return "400 (Bad Request)", 400


def run():
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socketio.run(app, host='0.0.0.0', port=5000)


def start():
    daemon = threading.Thread(target=run, daemon=True)
    daemon.setDaemon(True)
    daemon.start()
