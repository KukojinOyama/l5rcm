#!/usr/bin/python

import os

# global cache
_cache_names = {}

def parse_rtk(rtk):
    tk = rtk.split('k')
    if len(tk) != 2:
        return 0, 0
    return int(tk[0]), int(tk[1])
    
def format_rtk(r, k):
    bonus = 0
    if r > 10:
        k += (r-10)
        r = 10
    if k > 10:
        bonus = (k-10)*2
        k = 10
    if bonus:
        return '%dk%d + %d' % (r, k, bonus)
    else:
        return '%dk%d' % (r, k)
    
def get_random_name(path):
    global _cache_names
    
    names = []
    if path in _cache_names:
        names = _cache_names[path]
    else:
        f = open(path, 'rt')
        for l in f:
            if l.strip().startswith('*'):
                names.append( l.strip('* ') )
        f.close()
        _cache_names[path] = names
    
    i = ( ord(os.urandom(1)) + ( ord(os.urandom(1)) << 8) ) % len(names)
    return names[i]
    
