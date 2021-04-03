import vlc
import worker
import gui


vlc.stop()

gui.paint()

worker.start()

gui.loop()
