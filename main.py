from src import vlc, worker, gui, web
import json

settings = json.loads(open('settings.json', 'r').read())

vlc.stop()

gui.paint()

worker.start()

web.start(settings)

gui.loop()
