import os
import subprocess
import sys

if sys.platform == 'win32':
    _vlc = 'C:/Program Files/VideoLAN/VLC/vlc.exe'
    _dir = 'C:'
    _kill = 'taskkill /f /im vlc.exe >nul 2>&1'
else:
    _vlc = 'vlc'
    _dir = '/media'
    _kill = 'pkill -9 vlc'


def play(drive, files):
    stop()
    os.chdir(drive)
    #subprocess.Popen([_vlc, *files, '--loop', '--fullscreen', '--no-video-title', '-Idummy', '--mouse-hide-timeout=0', '--video-on-top'])


def stop():
    os.chdir(_dir)
    os.system(_kill)
