#!/usr/bin/env python3

import argparse
import os.path
import sys

import mutagen
from mpd import MPDClient

from rofi import Rofi
from .config import load_config
from .date_parser import LONG_TIME_AGO, get_epoch_from_date, get_epoch_as_year

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--artists', action='store_true', help='Start at a list of all albums. This is the default')
parser.add_argument('-b', '--albums', action='store_true', help='Start at a list of all albums')
parser.add_argument('-t', '--tracks', action='store_true', help='Start at a list of all tracks')
parser.add_argument('-g', '--genres', action='store_true', help='Start at a list of genres')
parser.add_argument('-l', '--playlists', action='store_true', help='Show a list of playlists to load')

parser.add_argument('-m', '--music-directory', help='Path to your music library')

parser.add_argument('-c', '--host', help='Use the specified MPD host')
parser.add_argument('-p', '--port', help='Use the specified MPD port')

parser.add_argument('--play', action='store_true', help='Start playback on add (overrides config)', dest='play_on_add',
                    default=None)
parser.add_argument('--noplay', action='store_false', help='Do not start playback on add (overrides config)',
                    dest='play_on_add', default=None)

parser.add_argument('-i', '--case-sensitive', action='store_true', help='Enable case sensitivity')

parser.add_argument('-r', '--args', nargs=argparse.REMAINDER, help='Command line arguments for rofi. '
                                                                   'Separate each argument with a space.')

args = parser.parse_args()


def select(data, prompt, rofi, select=None):
    index, key = rofi.select(prompt, data, select=select)

    if key == -1:
        sys.exit()

    return index


def select_host(hosts, rofi: Rofi):
    index = select([host['host'] for host in hosts], 'Select host', rofi)
    return hosts[index]


def select_artist(artists, rofi: Rofi):
    index = select(artists, 'Select artist', rofi)
    return artists[index]


def select_album(albums, rofi: Rofi):
    index = select(
        ['[%s] %s' % (get_epoch_as_year(int(get_tag('date', album))), get_tag('album', album)) for album in albums],
        'Select album', rofi)

    return albums[index]['album']


def select_genre(genres, rofi: Rofi):
    index = select(genres, 'Select genre', rofi)

    return genres[index]


def select_track(tracks, rofi: Rofi, discs=False, cycle=True):
    extras = ['All']
    if discs:
        disc_numbers = set([get_tag('disc', track) for track in tracks])
        if len(disc_numbers) > 1:
            extras.append('Disc...')

    display_tracks = extras + [
        '[%s.%s]  \t%s [%s - %s]' % (
            get_tag('disc', track),
            get_tag('track', track),
            get_tag('title', track),
            get_tag('album', track),
            get_tag('artist', track))
        for track in tracks]

    prev_index = -1
    first_cycle = True
    while cycle or first_cycle:
        index = select(display_tracks, 'Select track', rofi, select=prev_index + 1)

        prev_index = index
        first_cycle = False

        yield (extras + tracks)[index]


def select_disc(tracks, rofi: Rofi, music_library, cycle=True, enable_disc_names=True):
    discs = {}
    for track in tracks:
        disc_num = get_tag('disc', track)
        if disc_num not in discs:
            discs[disc_num] = (get_disc_name(track, music_library, enable_disc_names))

    display_discs = [{'num': num, 'name': name} for (num, name) in discs.items()]
    display_discs.sort(key=lambda x: int(x['num']))

    prev_index = -1
    first_cycle = True
    while cycle or first_cycle:
        index = select([disc['name'] for disc in display_discs], 'Select disc', rofi, select=prev_index + 1)

        prev_index = index
        first_cycle = False

        yield display_discs[index]['num']


def select_playlist(playlists, rofi: Rofi):
    display_playlists = [playlist['playlist'] for playlist in playlists]

    index = select(display_playlists, 'Select playlist', rofi)
    return playlists[index]


def get_album_date(client, album, artist=None):
    if artist:
        tracks = client.find('artist', artist, 'album', album)
    else:
        tracks = client.find('album', album)
    if len(tracks) > 0:
        for track in tracks:
            if 'date' in track:
                return get_epoch_from_date(get_tag('date', track))

    return LONG_TIME_AGO


def get_tag(tag: str, track):
    if tag == 'track' or tag == 'disc':
        func = int
        default = 1
    else:
        func = str
        default = 'N/A'

    if tag in track:
        value = track[tag]

        if type(value) == list:
            return func(value[0])
        else:
            return func(value)
    else:
        return default


def get_disc_name(track, music_library, enable_disc_names=True):
    name = 'Disc %s' % track.get('disc') or 1

    if enable_disc_names:
        tags = mutagen.File(os.path.join(music_library, get_tag('file', track)))
        if 'TSST' in tags:
            name += ': ' + tags['TSST'][0]
        if 'TXXX:TSST' in tags:
            name += ': ' + tags['TXXX:TSST'][0]

    return name


def get_album(client, rofi, albums, artist=None):
    dated_albums = [{'album': album, 'date': get_album_date(client, album, artist)} for album in albums]
    dated_albums.sort(key=lambda x: x['date'])
    return select_album(dated_albums, rofi)


def get_tracks(client, rofi):
    if args.playlists:
        tracks = client.listplaylists()
    elif args.tracks:
        tracks = client.find('(title != "")')
    elif args.albums:
        albums = client.list('album')
        album = get_album(client, rofi, albums)

        tracks = client.find('album', album)

    elif args.genres:
        genres = client.list('genre')
        genre = select_genre(genres, rofi)

        albums = client.list('album', '(genre == "%s")' % genre)
        album = get_album(client, rofi, albums)

        tracks = client.find('genre', genre, 'album', album)

    else:
        artists = client.list('artist')
        artist = select_artist(artists, rofi)

        albums = client.list('album', '(artist == "%s")' % artist)
        album = get_album(client, rofi, albums, artist)

        tracks = client.find('artist', artist, 'album', album)

    tracks.sort(key=lambda t: (
        get_tag('artist', t),
        get_tag('album', t),
        get_tag('disc', t),
        get_tag('track', t)
    ))

    return tracks


def run():
    config = load_config()

    music_directory = os.path.expanduser(args.music_directory or config['music_directory'])
    single_host_mode = args.host is not None or len(config['hosts']) == 1
    case_sensitive = args.case_sensitive or config['case_sensitive']

    cycle_tracks = config['tracks_keep_open']
    cycle_discs = config['discs_keep_open']

    rofi_args = args.args or []
    if not case_sensitive:
        rofi_args.append('-i')

    rofi = Rofi(rofi_args=rofi_args)

    if single_host_mode:
        if args.host:
            host = dict(host=args.host, port=args.port or 6600)
        else:
            host = config['hosts'][0]
    else:
        host = select_host(config['hosts'], rofi)

    client = MPDClient()
    client.connect(host['host'], host['port'])

    tracks = get_tracks(client, rofi)

    if args.playlists:
        playlist = select_playlist(tracks, rofi)
        client.load(playlist['playlist'])
    else:
        for track in select_track(tracks, rofi,
                                  discs=not (args.tracks or args.genres),
                                  cycle=cycle_tracks):
            if track == 'All':
                for track in tracks:
                    client.add(get_tag('file', track))

            elif track == 'Disc...':
                for disc in select_disc(tracks, rofi, music_directory, cycle=cycle_discs,
                                        enable_disc_names=config['enable_disc_names']):
                    disc_tracks = [track for track in tracks if get_tag('disc', track) == disc]

                    for track in disc_tracks:
                        client.add(get_tag('file', track))

                if not cycle_discs:
                    break

            else:
                client.add(get_tag('file', track))

    play_on_add = None
    if 'play_on_add' in config:
        play_on_add = config['play_on_add']

    if args.play_on_add is not None:
        play_on_add = args.play_on_add

    if play_on_add:
        if client.status()['state'] != 'play':
            client.play()
