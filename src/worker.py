from queue import Queue
from threading import Thread


def _task(q):
    import time
    from src import vlc, gui, drive, web

    while True:
        if not q.empty():
            vlc.stop()
            exit()

        gui.waiting()

        usb = drive.find()

        if usb is None:
            usb = web.storage
            if web.status() != 'play':
                time.sleep(5)
                continue
            files = drive.read(usb)
            if not len(files):
                time.sleep(5)
                continue
            mode = 'web'
        else:
            gui.reading()
            files = drive.read(usb)
            if not len(files):
                gui.empty()
                time.sleep(15)
                continue
            mode = 'usb'

        try:
            vlc.play(usb, files)
            gui.playing()
            while True:
                if mode == 'web' and (web.status() != 'play' or drive.find() != None):
                    break
                if mode == 'usb' and drive.find() != usb:
                    break
                if not q.empty():
                    vlc.stop()
                    exit()
                if not vlc.check():
                    break
                time.sleep(1)
        except Exception as e:
            print(e)
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
