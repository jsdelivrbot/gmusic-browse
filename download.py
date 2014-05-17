#!/usr/bin/env python

from os import getenv
from json import dumps
from getpass import getpass
from operator import itemgetter
from gmusicapi import Mobileclient

conf_filename = (getenv('HOME') or getenv('USERPROFILE')) + '/.gmusic'
retain_keys = ['rating', 'year', 'album', 'title', 'genre', 'playCount',
               'artist', 'albumArt']


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
    for i, item in enumerate(l):
        if 'albumArtRef' in item:
            l[i]['albumArt'] = item['albumArtRef'][0]['url']
        else:
            l[i]['albumArt'] = ''

        if 'artistArtRef' in item:
            l[i]['artistArt'] = item['artistArtRef'][0]['url']
        else:
            l[i]['artistArt'] = ''
        
    return l

def filter_keys(l, keys):
    return [{k: item[k] for k in keys if k in item} for item in l]


if __name__ == '__main__':
    api = connect_api()

    if api.is_authenticated():
        library = api.get_all_songs()
        library = normalize_urls(library)
        library = filter_keys(library, retain_keys)

        print dumps(library, sort_keys=True, indent=4, separators=(',', ': '))
        api.logout()
