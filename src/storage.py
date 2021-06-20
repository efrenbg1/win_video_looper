import os
from pathlib import Path
import mimetypes

directory = os.path.realpath(os.path.join(Path(__file__).parent, '../storage'))
if not os.path.exists(directory):
    os.makedirs(directory)

files = os.path.realpath(os.path.join(Path(__file__).parent, '../storage/files'))
if not os.path.exists(files):
    os.makedirs(files)

featured = os.path.realpath(os.path.join(Path(__file__).parent, '../storage/featured'))
if not os.path.exists(featured):
    os.makedirs(featured)


def read():
    global files, featured

    l1 = _read(files)
    l2 = _read(featured)

    l = []
    for f in l1:
        l.append(os.path.join('files', f))
        for f in l2:
            l.append(os.path.join('featured', f))
    if len(l) == 0:
        for f in l2:
            l.append(os.path.join('featured', f))

    return l


def _read(storage):
    try:
        videos = []
        for file in os.listdir(storage):
            mime = mimetypes.guess_type(file)
            if mime[0] is None:
                continue
            if mime[0].startswith('video'):
                videos.append(file)
            if mime[0].startswith('image'):
                videos.append(file)
        return videos
    except Exception as e:
        print(e)
        return []
