import os


def stop():
    os.system('taskkill /f /im msedge.exe >nul 2>&1')


def start():
    stop()
    os.system('start /b "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk http://localhost:5000/projector --edge-kiosk-type=fullscreen')
