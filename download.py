#!/usr/bin/env python

from os import getenv
from json import dumps
from getpass import getpass
from operator import itemgetter, xor
from gmusicapi import Mobileclient


# Turn this off to debug
compress_json = True

conf_filename = (getenv('HOME') or getenv('USERPROFILE')) + '/.gmusic'
song_keys = ['rating', 'year', 'album', 'title', 'genre', 'playCount', 'artist', 'recentTimestamp']
album_keys = ['year', 'album', 'genre', 'artist', 'albumArt', 'albumArtist', 'recentTimestamp']


def connect_api():
    api = Mobileclient()

    try:
        f = open(conf_filename, "r")
        email, password = [l.strip() for l in f.readlines()[:2]]
        logged_in = api.login(email, password)
        f.close()

    except:
        logged_in = False
        attempts = 0

        while not logged_in and attempts < 3:
            email = raw_input('Email: ')
            password = getpass()

            logged_in = api.login(email, password)
            attempts += 1

    return api

def normalize_urls(l):
    default_art = 'https://i.imgur.com/dwMmPDY.png'

    for i, item in enumerate(l):
        if 'albumArtRef' in item:
            l[i]['albumArt'] = item['albumArtRef'][0]['url']
        else:
            l[i]['albumArt'] = default_art

        if 'artistArtRef' in item:
            l[i]['artistArt'] = item['artistArtRef'][0]['url']
        else:
            l[i]['artistArt'] = default_art

    return l

def filter_keys(item, keys):
    return {k: item[k] for k in keys if k in item}

def filter_keys_list(l, keys):
    return [filter_keys(item, keys) for item in l]

def album_hash(album):
    hashkeys = ['album', 'artist', 'year']
    return reduce(xor, [hash(album[k]) for k in hashkeys])

def get_albums(library, keys):
    albums = []
    album_hashes = set()

    for song in library:
        album = filter_keys(song, keys)

        # Handle albums with various artists
        if album['albumArtist']:
            album['artist'] = album['albumArtist']
        del(album['albumArtist'])

        h = album_hash(album)
        if (h not in album_hashes) and album['album']:
            albums.append(album)
            album_hashes.add(h)
    return albums

def get_most_recent_played(songs, limit):
    sorted_songs = sorted(songs, key=itemgetter('recentTimestamp'), reverse=True)
    return sorted_songs[:limit]

def write_json(filename, data):
    try:
        f = open(filename, 'w')
        if compress_json:
            f.write(dumps(data))
        else:
            f.write(dumps(data, sort_keys=True, indent=2, separators=(',', ':')))
        f.close()
    except:
        print "ERROR: Unable to write", filename


if __name__ == '__main__':
    api = connect_api()

    if api.is_authenticated():
        library = normalize_urls(api.get_all_songs())
        all_songs = filter_keys_list(library, song_keys)
        all_albums = get_albums(library, album_keys)
        recent_songs = get_most_recent_played(all_songs, 10)

        write_json('songs.json', all_songs)
        write_json('albums.json', all_albums)
        write_json('recent.json', recent_songs)

        api.logout()
