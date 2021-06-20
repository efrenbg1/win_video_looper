from src import vlc, worker, gui, web, browser

vlc.stop()

browser.stop()

gui.paint()

worker.start()

web.start()

gui.loop()
