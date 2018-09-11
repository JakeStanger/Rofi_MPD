import json
import os
import stat
import sys
import time

from rofi import Rofi
from mpd import MPDClient


client = MPDClient()
client.connect('localhost', 6600)

db_age = time.time() - os.stat('database.json')[stat.ST_MTIME]

if db_age > 600:
    library_dict = {}

    library = client.listallinfo()
    for song in library:
        if 'artist' in song:
            artist = song['artist']
            if artist not in library_dict:
                library_dict[artist] = {}

            album = song['album']
            if album not in library_dict[artist]:
                library_dict[artist][album] = []

            library_dict[artist][song['album']].append(song['title'])

    with open('database.json', 'w') as f:
        f.write(json.dumps(library_dict, indent=4))

else:
    with open('database.json', 'r') as f:
        library_dict = json.loads(f.read())

r = Rofi()
index, key = r.select('Search artists', library_dict.keys())
if key == -1:
    sys.exit()

artist = [*library_dict][index]
albums = library_dict[artist]


index, key = r.select('Search %s' % artist, albums.keys())
if key == -1:
    sys.exit()

album = [*albums][index]
tracks = albums[album]

index, key = r.select('Search %s' % album, tracks)
