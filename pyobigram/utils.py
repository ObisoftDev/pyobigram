import requests
import time
import os
import re

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0

def get_url_file_name(url,req):
    try:
        if "Content-Disposition" in req.headers.keys():
            try:
                name = str(re.findall("filename=(.+)", req.headers["Content-Disposition"])[0])
                return name
            except:
                name = str(req.headers["Content-Disposition"]).replace('attachment; ','')
                name = name.replace('filename=','').replace('"','')
                return name
        else:
            import urllib
            urlfix = urllib.parse.unquote(url,encoding='utf-8', errors='replace')
            tokens = str(urlfix).split('/');
            return tokens[len(tokens)-1]
    except:
        import urllib
        urlfix = urllib.parse.unquote(url,encoding='utf-8', errors='replace')
        tokens = str(urlfix).split('/');
        return tokens[len(tokens)-1]
    return ''

def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size

def createID(count=8):
    from random import randrange
    map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    id = ''
    i = 0
    while i<count:
        rnd = randrange(len(map))
        id+=map[rnd]
        i+=1
    return id


def nice_time(delta):
    """
    Gets time delta in seconds and returns a pretty string
    representing it in the format of 1w2d9h16m44s
    """

    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 0

    seconds_in_minute = 60
    seconds_in_hour = 60 * seconds_in_minute
    seconds_in_day = 24 * seconds_in_hour
    seconds_in_week = 7 * seconds_in_day

    weeks = delta / seconds_in_week
    if weeks != 0:
        delta -= weeks * seconds_in_week

    days = delta / seconds_in_day
    if days != 0:
        delta -= days * seconds_in_day

    hours = delta / seconds_in_hour
    if hours != 0:
        delta -= hours * seconds_in_hour

    minutes = delta / seconds_in_minute
    if minutes != 0:
        delta -= minutes * seconds_in_minute

    seconds = delta

    out = ""
    if seconds:
        out = "%ss" % seconds + out
    if minutes:
        out = "%sm" % minutes + out
    if hours:
        out = "%sh" % hours + out
    if days:
        out = "%sd" % days + out
    if weeks:
        out = "%sw" % weeks + out

    if out == "":
        return "just now"
    return out