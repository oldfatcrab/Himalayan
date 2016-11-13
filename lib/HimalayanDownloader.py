from HTMLParser import HTMLParser
import json
from os import makedirs
from os.path import abspath, dirname, exists, join, normpath
import pycurl
import Queue
import re
import requests
import tempfile
import urllib2

class HimalayanDownloader:
    def __init__(self, eBookUrl, logger):
        self._logger = logger
        self._eBookUrl = eBookUrl
        self._failedTracksQueue = None
        self._downloadQueue = Queue.Queue()
        self._completedQueue = Queue.Queue()
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
        currPath = join(dirname(abspath(__file__)), '..')
        bookPath = normpath(join(currPath, self._bookName))
        self._logger.info('Files can be found in: ' + bookPath)
        if not exists(bookPath):
            makedirs(bookPath)
        self.fetchTracks()
        while self._trial < self._maxTrial:
            self._failedTracksQueue = Queue.Queue()
            while not self._downloadQueue.empty():
                track = self._downloadQueue.get()
                self.downloadTrack(track[0], track[1])
            if self._failedTracksQueue.empty():
                break
            else:
                self._downloadQueue = self._failedTracksQueue
                self._trail += 1

        self._logger.info('Finished downloading book <<' + self._bookName + '>>')
        return self._completedQueue

    def downloadTrack(self, url, fileName):
        self._logger.info('Downloading track: ' + fileName)
        self._logger.debug('Track URL: ' + url)
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
                self._completedQueue.put((tmpFilePath, self._bookName, fileName))

    def fetchTracks(self):
        pageNum = 1
        trackQueue= Queue.Queue()
        while True:
            pageUrl = self._eBookUrl + '?page=%d' % pageNum
            self._logger.debug('Fetching page: ' + pageUrl)
            response = urllib2.urlopen(pageUrl)
            html = response.read()
            self._logger.debug('Analyzing page: ' + pageUrl)
            pattern = re.compile('<a class="title" href="(.*?)" hashlink title="(.*?)">', re.S)
            results = re.findall(pattern, html)
            if not results:
                break
            for result in results:
                trackQueue.put(result)
            pageNum += 1
        indexLength = len(str(trackQueue.qsize()))
        index = 0
        while not trackQueue.empty():
            index += 1
            track = trackQueue.get()
            jsonUrl = self._trackUrlDir + track[0].split('sound/')[-1] + '.json'
            self._logger.debug('Loading JSON: ' + jsonUrl)
            resp = requests.get(url=jsonUrl)
            data = json.loads(resp.text)
            fileName = self._bookName + '_' + str(index).zfill(indexLength) + '_'
            fileName += self._hp.unescape(track[1].decode('utf-8')).replace(':', '_')
            url = data['play_path']
            self._downloadQueue.put((url, fileName))

