import os
import mimetypes
import sys

if sys.platform == 'win32':
    import wmi
    c = wmi.WMI()

    def find():
        for disk in c.Win32_LogicalDisk():
            if disk.DriveType != 2:
                continue
            return disk.DeviceID
        return None
else:
    def find():
        for d in os.listdir('/media'):
            d = '/media/' + d
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
