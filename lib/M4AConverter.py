import ffmpy
from os.path import abspath, dirname, join, normpath
from os import remove

class M4AConverter:
    def __init__(self, logger):
        self._logger = logger
        self._currPath = join(dirname(abspath(__file__)), '..')

    def convert(self, inputFilePath, bookName, fileName):
        bookPath = normpath(join(self._currPath, bookName))
        outputOptions = ' -b:a 64k'
        metadata = {
            "title": fileName,
            "author": '',
            "album_artist": '',
            "album": bookName,
            "grouping": '',
            "composer": '',
            "year": '',
            "track": '',
            "comment": '',
            "genre": '',
            "copyright": '',
            "description": '',
            "synopsis": '',
            "show": '',
            "episode_id": '',
            "network": '',
            "lyrics": ''
        }
        for k, v in metadata.iteritems():
            outputOptions += ' -metadata '
            outputOptions += k
            outputOptions += '="'
            outputOptions += v
            outputOptions += '"'

        outputFileName = fileName + '.m4a' 
        outputFilePath = normpath(join(bookPath, outputFileName))
        self._logger.info('Converting ' + outputFileName)
        inputFilePath = inputFilePath.encode('utf-8')
        outputFilePath = outputFilePath.encode('utf-8')
        outputOptions = outputOptions.encode('utf-8')
        ff = ffmpy.FFmpeg(
            inputs = {inputFilePath: None},
            outputs = {outputFilePath: outputOptions},
            global_options = '-y -loglevel quiet'
        )
        try:
            ff.run()
        except ffmpy.FFRuntimeError as e:
            self._logger.error('ERROR occurred: ' + e.message)
        else:
            remove(inputFilePath)

