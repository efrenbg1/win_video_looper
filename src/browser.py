import os
import sys
import subprocess
import settings


def stop():
    if sys.platform == 'win32':
        os.system('taskkill /f /im msedge.exe >nul 2>&1')
    else:
        os.system('pkill -9 firefox')


def start():
    stop()
    if sys.platform == 'win32':
        os.system('start /b "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk https://{}/projector --edge-kiosk-type=fullscreen'.format(settings.domain))
    else:
        subprocess.Popen(['firefox', '-kiosk', '-private-window', 'https://{}/projector'.format(settings.domain)])
