#!/usr/bin/env python

from os import getenv
from json import dumps
from getpass import getpass
from operator import itemgetter
from gmusicapi import Mobileclient

conf_filename = (getenv('HOME') or getenv('USERPROFILE')) + '/.gmusic'
retain_keys = ['rating', 'year', 'album', 'title', 'genre', 'playCount', 'artist']
sort_key = 'year'


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

def filter_keys(l, keys):
    return [{k: item[k] for k in keys} for item in l]

def sort_list_by_key(l, key):
    return sorted(l, key=itemgetter(key), reverse=True) 


if __name__ == '__main__':
    api = connect_api()

    if api.is_authenticated():
        library = filter_keys(api.get_all_songs(), retain_keys)
        library = sort_list_by_key(library, sort_key)
        print dumps(library, sort_keys=True, indent=4, separators=(',', ': '))
        api.logout()
