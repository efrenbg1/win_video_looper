from src import vlc, gui, web, browser, storage
import threading
import time

_status = "pause"
_lstatus = threading.Lock()
_timeout = None


def play():
    global _lstatus, _status
    if web.casting():
        pause()
        return
    with _lstatus:
        _status = "play"
    vlc.stop()
    browser.stop()


def pause():
    global _lstatus, _status, _timeout
    with _lstatus:
        _status = "pause"
    vlc.stop()
    if _timeout != None:
        _timeout.cancel()
    _timeout = threading.Timer(15.0, play)
    _timeout.start()


def status():
    global _lstatus, _status
    with _lstatus:
        return _status


def _task():
    while True:

        gui.waiting()

        if status() == "pause":
            time.sleep(5)
            continue

        l = storage.read()

        if not len(l):
            time.sleep(5)
            continue

        try:
            vlc.play(storage.directory, l)
            gui.playing()
            while True:
                if status() == 'pause':
                    break
                if not vlc.check():
                    break
                time.sleep(1)
        except Exception as e:
            print(e)
            pass

        gui.paint()
        vlc.stop()


def start():
    daemon = threading.Thread(target=_task, daemon=True)
    daemon.setDaemon(True)
    daemon.start()
    play()
