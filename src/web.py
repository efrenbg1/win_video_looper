from flask import Flask, request, redirect, send_from_directory, render_template
from pathlib import Path
import os
import urllib
import time
import threading
from src import vlc, drive


hostname = os.environ['COMPUTERNAME']

app = Flask(__name__, template_folder="../static")

storage = os.path.realpath(os.path.join(Path(__file__).parent, '../videos'))
if not os.path.exists(storage):
    os.makedirs(storage)

_status = "pause"
_lstatus = threading.Lock()


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
    return render_template('login.html', hostname=hostname)


@app.route("/")
def root():
    global hostname
    if request.cookies.get('secret') != app.secret:
        return redirect('/login')
    videos = []
    for video in os.listdir(storage):
        date = os.path.getmtime(os.path.join(storage, video))
        date = time.localtime(date)
        date = time.strftime('%d/%m/%Y %H:%M ', date)
        videos.append({
            'filename': video,
            'date': date
        })
    return render_template('index.html', hostname=hostname, videos=videos, status=status())


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
    return redirect('/')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../static/', path)


@app.route('/watch/<path:path>')
def watch_videos(path):
    if request.cookies.get('secret') != app.secret:
        return "401 (Unauthorized)", 401
    return send_from_directory(storage, urllib.parse.quote(path))


@app.route('/download/<path:path>')
def download_videos(path):
    if request.cookies.get('secret') != app.secret:
        return "401 (Unauthorized)", 401
    return send_from_directory(storage, urllib.parse.quote(path), as_attachment=True)


@app.route('/upload', methods=["POST"])
def upload():
    if request.cookies.get('secret') != app.secret:
        return "401 (Unauthorized)", 401

    file = request.files.get('file')
    if file is None:
        return redirect('/?file')

    filename = urllib.parse.quote(file.filename)
    if filename in os.listdir(storage):
        return redirect('/?exists')

    path = os.path.join(storage, filename)
    if os.path.commonprefix((os.path.realpath(path), storage)) != storage:
        return redirect('/?path')

    if status() == "play":
        return redirect('/?status')

    file.save(path)
    return redirect('/?upload')


@app.route('/delete')
def delete():
    global _lstatus
    if request.cookies.get('secret') != app.secret:
        return "401 (Unauthorized)", 401

    file = request.args.get('filename')
    if file is None:
        return redirect('/?file')

    file = urllib.parse.quote(file)
    if file not in os.listdir(storage):
        return redirect('/?path')

    path = os.path.join(storage, file)
    if os.path.commonprefix((os.path.realpath(path), storage)) != storage:
        return redirect('/?path')

    if status() == "play":
        return redirect('/?status')

    os.remove(path)
    return redirect('/?delete')


def run(host, port):
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=host, port=port)


def start(settings):
    app.secret = settings['secret']
    daemon = threading.Thread(target=run, args=(settings['host'], settings['port'],), daemon=True)
    daemon.setDaemon(True)
    daemon.start()
