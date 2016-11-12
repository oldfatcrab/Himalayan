from HTMLParser import HTMLParser
import json
from os import makedirs
from os.path import exists, join, normpath
import pycurl
import re
import requests
import tempfile
import urllib2

class HimalayanDownloader:
    def __init__(self, eBookUrl, logger):
        self._logger = logger
        self._eBookUrl = eBookUrl
        self._failedTracks = None
        self._downloadList = []
        self._completedTracks = []
        self._maxTrial = 10
        self._trial = 0
        self._hp = HTMLParser()
        self._trackUrlDir = 'http://www.ximalaya.com/tracks/'
        self._bookName = self.getBookName()

    def getBookName(self):
        response = urllib2.urlopen(self._eBookUrl)
        html = response.read()
        pattern = re.compile('<h1>(.*?)</h1>', re.S)
        rawName = re.findall(pattern, html)[0].decode('utf-8')
        return self._hp.unescape(rawName).replace(':', '_')

    def download(self):
        self._logger.info('Downloading book <<' + self._bookName + '>>')
        if not exists(self._bookName):
            makedirs(self._bookName)
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
        return self._completedTracks

    def downloadTrack(self, url, fileName):
        self._logger.info('Downloading: ' + fileName)
        self._logger.debug('From URL: ' + url)
        tmpFileName = url.split('/')[-1]
        tmpFilePath = normpath(join(tempfile.gettempdir(), tmpFileName))
        with open(tmpFilePath, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, f)
            try:
                c.perform()
            except pycurl.error as e:
                self._logger.error('ERROR occurred: ' + e.message)
                self._logger.debug('Adding "' + fileName + '" to re-download tasks')
                self._failedTracks.append((url, fileName))
            else:
                c.close()
                self._completedTracks.append((tmpFilePath, self._bookName, fileName))

    def fetchTracks(self):
        pageNum = 1
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
            url = data['play_path']
            self._downloadList.append((url, fileName))
            index -= 1
        self._downloadList = self._downloadList[::-1]

