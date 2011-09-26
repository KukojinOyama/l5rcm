#!/usr/bin/python

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
    
