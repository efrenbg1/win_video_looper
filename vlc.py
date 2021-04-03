import os
import subprocess


def play(drive, files):
    stop()
    os.chdir(drive)
    subprocess.Popen(['C:/Program Files/VideoLAN/VLC/vlc.exe', *files, '--loop', '--fullscreen', '--no-video-title', '-Idummy', '--mouse-hide-timeout=0'])


def stop():
    os.chdir("C:")
    os.system("taskkill /f /im vlc.exe >nul 2>&1")
