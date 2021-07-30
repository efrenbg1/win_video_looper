from src import vlc, gui, browser, storage, fsm
import threading
import time


def play():
    if fsm.get() == "casting":
        vlc.stop()
        return
    fsm.set("play", timeout=5)
    vlc.stop()
    browser.stop()


def _task():
    while True:

        gui.waiting()

        if fsm.get() != "play":
            time.sleep(5)
            continue

        l = storage.read()

        if not len(l):
            time.sleep(5)
            continue

        try:
            browser.stop()
            vlc.play(storage.directory, l)
            gui.playing()
            while True:
                if fsm.get() != 'play':
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
