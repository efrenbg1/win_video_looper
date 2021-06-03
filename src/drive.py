import os
import mimetypes
import sys

if sys.platform == 'win32':
    import subprocess

    def find():
        out = subprocess.Popen(['wmic', 'logicaldisk', 'where', 'drivetype=2', 'get', 'DeviceID'],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, _ = out.communicate()
        if b"DeviceID  \r\r\n" in stdout:
            return stdout[13:15].decode('utf-8')
        return None
else:
    def find():
        for d in os.listdir('/media/pi'):
            d = '/media/pi/' + d
            if not os.path.ismount(d):
                continue
            return d


def read(drive):
    try:
        videos = []
        for file in os.listdir(drive):
            mime = mimetypes.guess_type(file)
            if mime[0] is None:
                continue
            if mime[0].startswith('video'):
                videos.append(file)
        return videos
    except Exception as e:
        print(e)
        return []
