#!/usr/binhon

import pip
import sys

from DownloadLogger import DownloadLogger
from HimalayanDownloader import HimalayanDownloader

def setup():
    packages = ['ffmpy']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            logger.warning('Package "' + package + '" not found, installing...')
            pip.main(['install', '--user', package])

def main(argv):
    setup()
    logger = DownloadLogger()
    logger.info('Debug log can be found at: ' + logger.getLogPath())
    for eBookUrl in argv:
        downloader = HimalayanDownloader(eBookUrl, logger)

if __name__ == "__main__":
   main(sys.argv[1:])
