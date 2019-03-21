#!/usr/bin/env python3
import datetime
import json
import os
import stat
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Optional

from rofi import Rofi
from mpd import MPDClient
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--albums', action='store_true', help='Start at a list of all albums')
parser.add_argument('-t', '--tracks', action='store_true', help='Start at a list of all tracks')
parser.add_argument('-a', '--all', action='store_true', help='Search all artists, albums and tracks')

parser.add_argument('-f', '--full', action='store_true', help='Force display of full strings [TODO Implement]')
parser.add_argument('-n', '--no-full', action='store_true', help='Force disable display full strings [TODO Implement]')

parser.add_argument('-c', '--host', help='Use the specified MPD host')
parser.add_argument('-p', '--port', help='Use the specified MPD port')
parser.add_argument('-d', '--database', help='Use the specified database '
                                             '(note this is the database for Rofi-MPD and not MPD\'s database. '
                                             'You probably do not want to do this).')

parser.add_argument('-i', '--case-sensitive', action='store_true', help='Enable case sensitivity')

parser.add_argument('-r', '--args', nargs=argparse.REMAINDER, help='Command line arguments for rofi. '
                                                                   'Separate each argument with a space.')

args = parser.parse_args()

if args.full and args.no_full:
    print('You cannot use full and no-full together.')
    sys.exit()

short: Optional[bool] = None  # TODO Implement this down below
if args.full:
    short = False
elif args.no_full:
    short = True

host = args.host or 'localhost'
port = args.port or '6600'

database = args.database or str(Path.home()) + '/.local/share/main/database.json'
if '/' not in database:  # Handle when same directory filenames are passed
    database = './' + database

cache_timeout = 600

rofi_args = args.args or []
if not args.case_sensitive:
    rofi_args.append('-i')

selection_list = []


class ItemType(Enum):
    artist = 'artist'
    album = 'album'
    track = 'track'
    disc = 'disc'


LONG_TIME_AGO = -99999999999
UNKNOWN_ALBUM = '[Unknown Album]'


def get(data, key):
    """
    Since MPD supports any tag being a list,
    we want to just get the first one.

    Most of the time this is due to tagging issues
    """
    prop = data[key]
    if isinstance(prop, list):
        return prop[0]

    return prop


def get_epoch_as_year(epoch: int):
    if epoch == LONG_TIME_AGO:  # If album is missing year
        return 0
    return time.strftime('%Y', time.localtime(epoch))


def get_album_release_epoch(album=None, song_data=None):
    if not song_data:
        global selection_list
        song_data = filter(lambda x: x['type'] == ItemType.track
                                     and (x['data']['artist'] == album['data']['artist'])
                                     and (x['data']['album'] == album['data']['album']), selection_list)

        song_data = [*song_data][0]
    # Put undated albums at the top
    if 'date' not in song_data:
        return LONG_TIME_AGO
    else:
        date = song_data['date']

        # Handle multi-tagged dates
        if isinstance(date, list):
            date = date[0]

        if date.isnumeric():
            year = int(date)
            if year < 1 or year > 9999:
                year = 1
            epoch = datetime.datetime(year, 1, 1)
        else:
            split_char: str
            if '-' in date:
                split_char = '-'
            elif '.' in date:
                split_char = '.'
            date_list = date.split(split_char)

            while len(date_list) < 3:
                date_list.append(1)

            # Very basic date validation and correction
            year = int(date_list[0])
            month = int(date_list[1])
            day = int(date_list[2])
            if year < 1 or year > 9999:
                year = 1
            if month < 1 or month > 12:
                month = 1
            if day < 1 or day > 31:
                day = 1

            try:
                epoch = datetime.datetime(year, month, day)
            except ValueError:
                return LONG_TIME_AGO

        return int(epoch.replace(tzinfo=datetime.timezone.utc).timestamp())


client = MPDClient()
client.connect(host, port)

# Check if database exists and is young enough to use
if os.path.isfile(database):
    reload = time.time() - os.stat(database)[stat.ST_MTIME] > cache_timeout
else:
    reload = True

if reload:
    library_dict = {}

    library = client.listallinfo()
    for song in library:
        # Make sure this is a song and not a directory
        if 'artist' in song:
            artist = song['artist']
            if artist not in library_dict:
                library_dict[artist] = {}

            # Handle songs with missing album tag
            if 'album' in song:
                album = song['album']
            else:
                album = UNKNOWN_ALBUM

            if album not in library_dict[artist]:
                library_dict[artist][album] = {
                    'epoch': get_album_release_epoch(song_data=song),
                    'songs': []
                }
            library_dict[artist][album]['songs'].append({key: get(song, key) for key in song})

    # Create config directory if it does not exist
    directory = os.path.dirname(database)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(database, 'w') as f:
        f.write(json.dumps(library_dict))

else:
    with open(database, 'r') as f:
        library_dict = json.loads(f.read())

r = Rofi(rofi_args=rofi_args)


def get_display_string(item, full_album, full_track):
    item_type = item['type']
    item_data = item['data']

    if item_type == ItemType.artist:
        return item_data
    elif item_type == ItemType.album:
        return '[%s] %s%s' % (get_epoch_as_year(item_data['epoch']),
                              item_data['artist'] + ' - ' if full_album else '', item_data['album'])
    elif item_type == ItemType.track:
        if 'text' in item_data:
            return item_data['text']
        return '%s.%s %s- %s' % (item_data['disc'] if 'disc' in item_data else '1',
                                 item_data['track'] if 'track' in item_data else '0',
                                 '%s - %s ' % (item_data['artist'] if 'artist' in item_data else '[Unknown Artist]',
                                               item_data['album'] if 'album' in item_data else '[Unknown Album]'),
                                 item_data['title']) \
            if full_track else item_data['title']

    elif item_type == ItemType.disc:
        return item_data['text']


def select(title, data, full_album=False, full_track=True, discs=None):
    if discs and type(discs) is not set:
        items = discs
    else:
        items = data

    index, key = r.select('Search %s' % title, [get_display_string(item, full_album, full_track)
                                                for item in items])
    # Escape pressed
    if key == -1:
        sys.exit()

    selected = items[index]

    selected_type = selected['type']
    selected_data = selected['data']

    global selection_list

    if selected_type == ItemType.artist:
        select_album(selection_list, selected_data)

    elif selected_type == ItemType.album:
        select_track(selection_list, selected_data['artist'], selected_data['album'])

    elif selected_type == ItemType.track:
        if 'text' in selected_data:
            text = selected_data['text']
            if text == 'All':
                num = 1
                print(data[1])
                if 'text' in data[1]['data'] and data[1]['data']['text'] == 'Disc...':
                    num = 2
                for track in data[num:]:
                    client.add(track['data']['file'])
            elif text == 'Disc...':
                select_disc(data, discs, selected_data['album'])

        else:
            client.add(selected_data['file'])

    elif selected_type == ItemType.disc:
        data = [*filter(lambda x: int(x['data']['disc']) == selected_data['value'], data[2:])]
        for track in data:
            client.add(track['data']['file'])


def select_artist(data, title=None):
    data = filter(lambda x: x['type'] == ItemType.artist, data)
    select(title or 'All Artists', [*data])


def select_album(data, artist: Optional[str] = None, full_album=False):
    data = filter(lambda x: x['type'] == ItemType.album and (x['data']['artist'] == artist if artist else True), data)
    data = sorted([*data], key=lambda x: x['data']['epoch'])
    select(artist or 'All Albums', data, full_album=full_album)


def select_track(data, artist: Optional[str] = None, album: Optional[str] = None, full_track=False):
    data = filter(lambda x: x['type'] == ItemType.track
                            and (x['data']['artist'] == artist if artist else True)
                            and (x['data']['album'] == album if album else True), data)

    data = sorted([*data],
                  key=lambda x: (int(x['data']['disc'] if 'disc' in x['data'] else 1),
                                 int(x['data']['track']) if 'track' in x['data'] else 0))

    discs: set
    num_discs: int = 1
    if album:
        # Get number of discs in album
        discs = {*map(lambda x: int(x['data']['disc']) if 'disc' in x['data'] else 1, data)}
        num_discs = len(discs)

        if num_discs > 1:
            data = [{'type': ItemType.track, 'data': {'text': 'Disc...', 'album': album}}] + data
        data = [{'type': ItemType.track, 'data': {'text': 'All'}}] + data

    select(album or 'All Tracks', data, full_track=full_track, discs=discs if num_discs > 1 else None)


def select_disc(data, discs, album: str):
    discs = [*map(lambda x: {'type': ItemType.disc, 'data': {'text': 'Disc %r' % x, 'value': x}}, discs)]
    select('Discs for %s' % album, data, discs=discs)


def run():
    for artist in library_dict:
        selection_list.append({'type': ItemType.artist, 'data': artist})
        for album in library_dict[artist]:
            selection_list.append({'type': ItemType.album, 'data': {'artist': artist, 'album': album,
                                                                    'epoch': library_dict[artist][album]['epoch']}})
            for track in library_dict[artist][album]['songs']:
                if 'album' not in track:
                    track['album'] = UNKNOWN_ALBUM
                selection_list.append({'type': ItemType.track, 'data': track})

    if args.all:
        select('All', selection_list, full_album=True)
    elif args.albums:
        select_album(selection_list, full_album=True)
    elif args.tracks:
        select_track(selection_list, full_track=True)
    else:
        select_artist(selection_list)


if __name__ == "__main__":
    run()
