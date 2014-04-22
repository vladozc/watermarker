import logging
import os

from PIL import Image


logger = logging.getLogger()


class BaseWriter(object):
    '''Base class for writers. It is responsible for ...
    

    '''

    def __init__(self, paths, destination, format, wm, suffix='_watermarked'):
        '''
        :param list paths:
            Filepaths/folders to be processed.

        :param str destination:
            Destination where watermarked images will be stored.

        :param str format:
            Output format.

        :param watermarks.core.watermark wm:
            Watermark instance.

        :param str suffix:
            Suffix added to generated files. If set to empty string,
            generated image will overwrite original image.
        '''
        self.paths = paths
        self.destination = destination
        self.format = format
        self.wm = wm
        self.suffix = suffix

    def run(self):
        '''Runs the process.

        :return:
            List of generated files.
        :rtype: list
        '''
        processed = []
        for path in self.paths:
            if not os.path.exists(path):
                logger.error('Path "%s" does not exist! (skip)', path)
            elif os.path.isdir(path):
                processed.extend(self._process_dir(path))
            elif os.path.isfile(path):
                processed.append(self._process_file(path))
            else:
                raise NotImplementedError('Cannot determine type of %s', path)
        return filter(None, processed)

    def _process_dir(self, dirpath):
        processed = []
        for filename in os.listdir(dirpath):
            full_filepath = os.path.join(dirpath, filename)
            if os.path.isfile(full_filepath):
                res = self._process_file(full_filepath)
                processed.append(res)
        return processed

    def _process_file(self, filepath):
        src_img = Image.open(filepath)
        if src_img.format not in self.allowed_formats:
            logger.warning('File "%s" is in not allowed format. (skip)', filepath)
            return

        if src_img.mode in self.allowed_modes:
            base_name, _ = os.path.splitext(os.path.basename(filepath))
            logger.info('Processing file "%s"', filepath)
            dst_filepath = os.path.join(self.destination, '%s%s.%s' % (base_name, self.suffix, self.format))
            dst_img = self._create_watermarked(src_img)
            dst_img.save(dst_filepath)
            logger.info('Generated file "%s".', dst_filepath)
            return dst_filepath
        else:
            logger.warning('File "%s" is in unsupported mode "%s". (skip)', filepath, src_img.mode)

    def _create_watermarked(self, src_img):
        raise NotImplementedError()