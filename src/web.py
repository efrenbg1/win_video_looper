from flask import Flask, request, redirect, send_from_directory, render_template
from pathlib import Path
import os
import urllib
import time
import threading
from src import drive


hostname = os.environ['COMPUTERNAME']

app = Flask(__name__, template_folder="../static")

storage = os.path.realpath(os.path.join(Path(__file__).parent, '../videos'))
if not os.path.exists(storage):
    os.makedirs(storage)

status = "pause"
lstatus = threading.Lock()


@app.route('/login')
def login():
    if request.cookies.get('secret') == app.secret:
        return redirect('/')
    return render_template('login.html', hostname=hostname)


@app.route("/")
def root():
    global hostname, status, lstatus
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
    with lstatus:
        return render_template('index.html', hostname=hostname, videos=videos, status=status)


@app.route("/playpause")
def playpause():
    global status, lstatus
    if request.cookies.get('secret') != app.secret:
        return redirect('/login')
    with lstatus:
        if status == "play":
            status = "pause"
        else:
            status = "play"
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

    file.save(path)
    return redirect('/?upload')


@app.route('/delete')
def delete():
    if request.cookies.get('secret') != app.secret:
        return "401 (Unauthorized)", 401

    file = request.args.get('filename')
    print(file)
    if file is None:
        return redirect('/?file')

    file = urllib.parse.quote(file)
    print(file)
    if file not in os.listdir(storage):
        return redirect('/?path')

    path = os.path.join(storage, file)
    print(os.path.realpath(path))
    if os.path.commonprefix((os.path.realpath(path), storage)) != storage:
        return redirect('/?path')

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


def read():
    global status, lstatus
    with lstatus:
        if status == "play":
            return drive.read(storage)
        else:
            return []
