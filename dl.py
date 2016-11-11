#!/usr/bin/python

import HTMLParser
import json
import pip
import pycurl
import re
import requests
import sys
import urllib2

def setup():
    packages = ['ffmpy']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print '*** Package "', package, '" not found, installing...'
            pip.main(['install', '--user', package])     

def downloadTrack(url, filename, failedTracks):
    with open(filename, 'wb') as f:
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, f)
        print '*** Downloading: "', filename, '" from URL: ', url
        try:
            c.perform()
        except pycurl.error, error:
            errno, errstr = error
            print '!!! ERROR occurred: ', errstr
            print '!!! Adding "', failanme, '" to re-download task'
            failedTracks.append((url, filename))
        else:
            c.close()

def downloadBook(eBookUrl, failedTracks):
    tracks = []
    pageNum = 1
    response = urllib2.urlopen(eBookUrl)
    html = response.read()
    pattern = re.compile('<h1>(.*?)</h1>', re.S)
    bookName = HTMLParser.HTMLParser().unescape(re.findall(pattern, html)[0].decode('utf-8')).replace(':', '_')
    print bookName
    while True:
        response = urllib2.urlopen(eBookUrl + '?page=%d' % pageNum)
        html = response.read()
        pattern = re.compile('<a class="title" href="(.*?)" hashlink title="(.*?)">', re.S)
        results = re.findall(pattern, html)
        if not results:
            break
        tracks = tracks + results
        pageNum += 1
    index = len(tracks)
    indexLength = len(str(index))
    while index:
        track = tracks.pop()
        resp = requests.get(url='http://www.ximalaya.com/tracks/' + track[0].split('sound/')[-1] + '.json')
        data = json.loads(resp.text)
        filename = bookName + '_' + str(index).zfill(indexLength) + '_'
        filename += HTMLParser.HTMLParser().unescape(track[1].decode('utf-8')).replace(':', '_')
        filename += '.' + data['play_path'].split('.')[-1]
        url = data['play_path']
        downloadTrack(url, filename, failedTracks)
        index -= 1
        break


def main(argv):
    setup()
    failedTracks = []
    for eBookUrl in argv:
        downloadBook(eBookUrl, failedTracks)
    return 0
    trialCounter = 10
    while trialCounter:
        newFailedTracks = []
        for url, filename in failedTracks:
            downloadTrack(url, filename)
        failedTracks = newFailedTracks
        trialCounter -= 1
    if failedTracks:
        print '\n\n\n!!! The following tracks cannot be downloaded successfully'
        print '!!! Please manually download them:'
        print '\n'.join([failedTrack[1] for failedTrack in failedTracks])
        print '!!! End of failure list'

if __name__ == "__main__":
   main(sys.argv[1:])
