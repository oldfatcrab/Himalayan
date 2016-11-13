#!/usr/binhon

import sys
import Queue

from lib.DownloadLogger import DownloadLogger
from lib.HimalayanDownloader import HimalayanDownloader
from lib.M4AConverter import M4AConverter
import lib.setup

def main(argv):
    logger = DownloadLogger()
    converter = M4AConverter(logger)
    logger.info('Debug log can be found at: ' + logger.getLogPath())
    completedTracks = []
    for eBookUrl in argv:
        downloader = HimalayanDownloader(eBookUrl.split('?')[0], logger)
        completedQueue = downloader.download()
        while not completedQueue.empty():
            completedTrack = completedQueue.get()
            converter.convert(completedTrack[0], completedTrack[1], completedTrack[2])

if __name__ == "__main__":
    main(sys.argv[1:])

