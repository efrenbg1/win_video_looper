from src import vlc, worker, gui, web
import settings

vlc.stop()

gui.paint()

worker.start()

web.start(settings.secret)

gui.loop()
