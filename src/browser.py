import os
import sys
import subprocess
import settings


def stop():
    if sys.platform == 'win32':
        os.system('taskkill /f /im msedge.exe >nul 2>&1')
    else:
        os.system('pkill -9 chromium')


def start():
    stop()
    if sys.platform == 'win32':
        os.system('start /b "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk https://{}/projector --edge-kiosk-type=fullscreen'.format(settings.domain))
    else:
        subprocess.Popen(['chromium-browser', '--start-fullscreen', '--kiosk', 'http://localhost:5000/projector'])