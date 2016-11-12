#!/usr/binhon

import sys

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
        downloader = HimalayanDownloader(eBookUrl, logger)
        completedTracks = downloader.download()
    for completedTrack in completedTracks:
        converter.convert(completedTrack[0], completedTrack[1], completedTrack[2])

if __name__ == "__main__":
    main(sys.argv[1:])

