#!/usr/bin/env python

from os import getenv
from json import dumps
from getpass import getpass
from operator import itemgetter
from gmusicapi import Mobileclient

conf_filename = (getenv('HOME') or getenv('USERPROFILE')) + '/.gmusic'
song_keys = ['rating', 'year', 'album', 'title', 'genre', 'playCount', 'artist']
album_keys = ['year', 'album', 'genre', 'artist', 'albumArt']


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

def get_albums(library, keys):
    albums = []
    for song in library:
        album = filter_keys(song, keys)
        if album not in albums:
            albums.append(album)
    return albums

def write_json(filename, data):
    try:
        f = open(filename, 'w')
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

        write_json('songs.json', all_songs)
        write_json('albums.json', all_albums)
        
        api.logout()
