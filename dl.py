#!/usr/binhon

import setup
import sys

from DownloadLogger import DownloadLogger
from HimalayanDownloader import HimalayanDownloader
from M4AConverter import M4AConverter

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

