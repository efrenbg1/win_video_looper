from src import vlc, worker, gui


vlc.stop()

gui.paint()

worker.start()

gui.loop()
