import os
import mimetypes
import wmi

c = wmi.WMI()


def read(drive):
    videos = []
    for file in os.listdir(drive):
        mime = mimetypes.guess_type(file)
        if mime[0] is None:
            continue
        if mime[0].startswith('video'):
            videos.append(file)
    return videos


def find():
    for disk in c.Win32_LogicalDisk():
        if disk.DriveType != 2:
            continue
        return disk.DeviceID
    return None
