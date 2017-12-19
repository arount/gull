#!/usr/env/bin python


import os
import shutil

from gull.gullreader import GullReader


class Attachment(object):
    '''
    An attachment is a commited file.
    This class exposes easy way to manipulate it (read, write, copy)

    Because of Gull's architecture, each time a method tries to access
    file the right revision will be checkouted to ensure file's presence.
    '''


    def __init__(self, filename, _parent):
        '''
        Initialize instance by saving file name and commit hash.
        The absolute path of the filename would be computed here
        too in order to access easily to filehandler.

            filename     Path to file.
            _parent      Gull's Entity instance related with.
        '''
        self.commit_id = _parent.commit_id
        self.filename = filename

        greader = GullReader.get_instance()
        self._realpath = os.path.join(
            greader.repo.working_dir,
            self.filename
        )

        # Compute URLs (front-end path) and paths (backend/filesystem path)
        self.urls = []
        self.paths = []
        for url in greader.config['urls']['medias']:
            # Urls should access to all metadata
            args = _parent.__dict__.copy()
            args.update(self.__dict__)

            url = os.path.join(
                greader.config['filesystem']['medias'],
                url.format(**args)
            )
            path = os.path.join(
                greader.config['filesystem']['base'],
                url
            )

            self.urls.append(url)
            self.paths.append(path)


    def copyfile(self, dest):
        '''
        First copy method, it uses shutil.copy.
            dest    Destination file path.
        '''
        shutil.copy(self._get_file(), dest)


    def read(self, mode='rb', **kwargs):
        '''
        Read file
            mode      Opening mode
            kwargs    Any arguments that could be sent though `open()`.
        '''
        return self.filehandler(mode='rb', **kwargs).read()


    def write(self, output_path, mode='wb', **kwargs):
        '''
        Second copy method, using `filehandler.write()`.
            output_path    Destination path
            mode           Opening mode
            kwargs         Any arguments that could be sent though `open()`
        '''
        readmode = mode.replace('w', 'r')
        with open(output_path, mode=mode, **kwargs) as fh:
            fh.write(self.read(mode=readmode))


    def filehandler(self, mode='rb', **kwargs):
        '''
        Returns file handler.
        Usage of this method to access file handler is the only one recommended
        because its checkout the right revision.

            mode      Opening mode
            kwargs    Any arguments that could be sent though `open()`
        '''
        self._get_file()
        return open(self._realpath, mode=mode, **kwargs)


    def _get_file(self):
        '''
        Checkout revision and returns absolute path of file
        '''
        greader = GullReader.get_instance()
        greader.git.checkout(self.commit_id)
        return self._realpath

