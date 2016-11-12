from HTMLParser import HTMLParser
import json
from os.path import normpath, dirname, abspath, join, exists
import os
import pycurl
import re
import requests
import urllib2

class HimalayanDownloader:
    def __init__(self, eBookUrl, logger):
        self._logger = logger
        self._eBookUrl = eBookUrl
        self._failedTracks = None
        self._downloadList = []
        self._maxTrial = 10
        self._trial = 0
        self._hp = HTMLParser()
        self._trackUrlDir = 'http://www.ximalaya.com/tracks/'
        self._bookName = self.getBookName()
        self.downloadBook()

    def getBookName(self):
        response = urllib2.urlopen(self._eBookUrl)
        html = response.read()
        pattern = re.compile('<h1>(.*?)</h1>', re.S)
        rawName = re.findall(pattern, html)[0].decode('utf-8')
        return self._hp.unescape(rawName).replace(':', '_')

    def downloadBook(self):
        self._logger.info('Downloading book <<' + self._bookName + '>>')
        if not exists(self._bookName):
            os.makedirs(self._bookName)
        self.fetchTracks()
        while self._trial < self._maxTrial:
            self._failedTracks = []
            for track in self._downloadList:
                self.downloadTrack(track[0], track[1])
            if self._failedTracks:
                self._downloadList = self._failedTracks
            else:
                break
        self._logger.info('Finished downloading book <<' + self._bookName + '>>')

    def downloadTrack(self, url, filePath):
        with open(filePath, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            self._logger.info('Downloading: ' + filePath)
            self._logger.debug('From URL: ' + url)
            try:
                c.perform()
            except pycurl.error, error:
                errno, errstr = error
                self._logger.error('ERROR occurred: ' + errstr)
                self._logger.debug('Adding "' + failanme + '" to re-download task')
                self._failedTracks.append((url, filePath))
            else:
                c.close()

    def fetchTracks(self):
        pageNum = 1
        bookPath = normpath(join(dirname(abspath(__file__)), self._bookName))
        jsonList = []
        while True:
            response = urllib2.urlopen(self._eBookUrl + '?page=%d' % pageNum)
            html = response.read()
            pattern = re.compile('<a class="title" href="(.*?)" hashlink title="(.*?)">', re.S)
            results = re.findall(pattern, html)
            if not results:
                break
            jsonList += results
            pageNum += 1
        index = len(jsonList)
        indexLength = len(str(index))
        while index:
            track = jsonList.pop()
            url = self._trackUrlDir + track[0].split('sound/')[-1] + '.json'
            resp = requests.get(url=url)
            data = json.loads(resp.text)
            fileName = self._bookName + '_' + str(index).zfill(indexLength) + '_'
            fileName += self._hp.unescape(track[1].decode('utf-8')).replace(':', '_')
            fileName += '.' + data['play_path'].split('.')[-1]
            url = data['play_path']
            filePath = normpath(join(bookPath, fileName))
            self._downloadList.append((url, filePath))
            index -= 1
        self._downloadList = self._downloadList[::-1]

