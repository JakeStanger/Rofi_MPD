import datetime
import json
import os
import stat
import sys
import time
from collections import OrderedDict

from rofi import Rofi
from mpd import MPDClient

host = 'localhost'
port = '6600'
database = 'database.json'
cache_timeout = 600
rofi_args = []


def get_album_release_epoch(x):
    song_data = x[1][0]
    if 'date' not in song_data:
        return -99999999999
    else:
        date = song_data['date']
        if date.isnumeric():
            year = int(date)
            epoch = datetime.datetime(year, 1, 1)
        else:
            split_char: str
            if '-' in date:
                split_char = '-'
            elif '.' in date:
                split_char = '.'
            year, month, day = date.split(split_char)
            epoch = datetime.datetime(int(year), int(month), int(day))

        return int(epoch.timestamp())


client = MPDClient()
client.connect(host, port)

if os.path.isfile(database):
    reload = time.time() - os.stat(database)[stat.ST_MTIME] > cache_timeout
else:
    reload = True

if reload:
    library_dict = {}

    library = client.listallinfo()
    for song in library:
        if 'artist' in song:
            artist = song['artist']
            if artist not in library_dict:
                library_dict[artist] = {}

            if 'album' in song:
                album = song['album']
            else:
                album = "[Unknown]"

            if album not in library_dict[artist]:
                library_dict[artist][album] = []

            library_dict[artist][album].append(song)

    with open(database, 'w') as f:
        f.write(json.dumps(library_dict))

else:
    with open(database, 'r') as f:
        library_dict = json.loads(f.read())

r = Rofi(rofi_args=rofi_args)
index, key = r.select('Search artists', library_dict.keys())
if key == -1:
    sys.exit()

artist = [*library_dict][index]
albums = OrderedDict(library_dict[artist])
albums = sorted(albums.items(), key=lambda x: get_album_release_epoch(x))


index, key = r.select('Search %s' % artist, [album[0] for album in albums])
if key == -1:
    sys.exit()

album = albums[index][0]

tracks = albums[index][1]
tracks = sorted(tracks, key=lambda x: (int(x['disc'] if 'disc' in x else 1), int(x['track']) if 'track' in x else 0))
tracks = ["All"] + tracks

index, key = r.select('Search %s' % album, ['%s.%s - %s' % (t['disc'] if 'disc' in t else '1', t['track'], t['title'])
                                            if isinstance(t, dict)
                                            else t for t in tracks])

if index == 0:
    for track in tracks[1:]:
        client.add(track['file'])
    sys.exit()

track = [*tracks][index]
client.add(track['file'])
