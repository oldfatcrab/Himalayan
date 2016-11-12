from os.path import normpath, join
import logging
import tempfile

class DownloadLogger:
    def __init__(self):
        self._logger = logging.getLogger('DownloadLogger')
        self._logger.setLevel(logging.DEBUG)

        self._logPath = normpath(join(tempfile.gettempdir(), 'himalayan.log'))

        self._fh = logging.FileHandler(self._logPath)
        self._fh.setLevel(logging.DEBUG)

        self._ch = logging.StreamHandler()
        self._ch.setLevel(logging.INFO)

        self._formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        self._ch.setFormatter(self._formatter)
        self._fh.setFormatter(self._formatter)

        self._logger.addHandler(self._ch)
        self._logger.addHandler(self._fh)

    def getLogPath(self):
        return self._logPath

    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        self._logger.info(msg)

    def warn(self, msg):
        self._logger.warn(msg)

    def error(self, msg):
        self._logger.error(msg)

    def critical(self, msg):
        self._logger.critical(msg)

