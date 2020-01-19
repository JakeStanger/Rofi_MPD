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

parser.add_argument('-m', '--music-directory', help='Path to your music library')

parser.add_argument('-c', '--host', help='Use the specified MPD host')
parser.add_argument('-p', '--port', help='Use the specified MPD port')

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
    index = select(['[%s] %s' % (get_epoch_as_year(album['date']), album['album']) for album in albums],
                   'Select album', rofi)

    return albums[index]['album']


def select_genre(genres, rofi: Rofi):
    index = select(genres, 'Select genre', rofi)

    return genres[index]


def select_track(tracks, rofi: Rofi, discs=False, cycle=True):
    extras = ['All']
    if discs:
        disc_numbers = set([track['disc'] if 'disc' in track else 1 for track in tracks])
        if len(disc_numbers) > 1:
            extras.append('Disc...')

    display_tracks = extras + [
        '[%s.%s]  \t%s [%s - %s]' % (
            track['disc'] if 'disc' in track else 1,
            track['track'] if 'track' in track else 0,
            track['title'] if 'title' in track else 'N/A',
            track['album'] if 'album' in track else 'N/A',
            track['artist'] if 'artist' in track else 'N/A')
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
        disc_num = track.get('disc') or 1
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


def get_album_date(client, album, artist=None):
    if artist:
        tracks = client.find('artist', artist, 'album', album)
    else:
        tracks = client.find('album', album)
    if len(tracks) > 0:
        for track in tracks:
            if 'date' in track:
                return get_epoch_from_date(track['date'])

    return LONG_TIME_AGO


def get_disc_name(track, music_library, enable_disc_names=True):
    name = 'Disc %s' % track.get('disc') or 1

    if enable_disc_names:
        tags = mutagen.File(os.path.join(music_library, track['file']))
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
    if args.tracks:
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
        host = args.host = config['hosts'][0]
    else:
        host = select_host(config['hosts'], rofi)

    client = MPDClient()
    client.connect(host['host'], host['port'])

    tracks = get_tracks(client, rofi)

    for track in select_track(tracks, rofi,
                              discs=not (args.tracks or args.genres),
                              cycle=cycle_tracks):
        if track == 'All':
            for track in tracks:
                client.add(track['file'])

        elif track == 'Disc...':
            for disc in select_disc(tracks, rofi, music_directory, cycle=cycle_discs, enable_disc_names=config['enable_disc_names']):
                disc_tracks = [track for track in tracks if track.get('disc') == disc]

                for track in disc_tracks:
                    client.add(track['file'])

            if not cycle_discs:
                break

        else:
            client.add(track['file'])
