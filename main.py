from src import vlc, worker, gui, web, browser, fsm

vlc.stop()

browser.stop()

gui.paint()

fsm.start()

worker.start()

web.start()

gui.loop()
