from queue import Queue
from threading import Thread


def _task(q):
    import time
    import traceback
    from src import vlc, gui, drive, web

    while True:
        if not q.empty():
            vlc.stop()
            exit()

        gui.waiting()

        usb = drive.find()

        if usb is None:
            files = web.read()
            if not len(files):
                time.sleep(5)
                continue
            try:
                vlc.play(web.storage, files)
                gui.playing()
                while len(web.read()) and drive.find() == None:
                    if not q.empty():
                        vlc.stop()
                        exit()
                    time.sleep(1)
            except Exception:
                traceback.print_exc()
                vlc.stop()
                exit()
        else:
            gui.reading()
            files = drive.read(usb)
            if not len(files):
                gui.empty()
                time.sleep(15)
                continue
            try:
                vlc.play(usb, files)
                gui.playing()
                while drive.find() == usb:
                    if not q.empty():
                        vlc.stop()
                        exit()
                    time.sleep(1)
            except Exception:
                traceback.print_exc()
                vlc.stop()
                exit()

        gui.paint()
        vlc.stop()


_q = Queue()


def start():
    global _q
    Thread(target=_task, args=(_q, )).start()


def stop():
    global _q
    _q.put(True)
