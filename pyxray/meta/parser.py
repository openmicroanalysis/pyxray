""""""

# Standard library modules.
import os
import abc
import json
import hashlib
import logging
logger = logging.getLogger(__name__)

# Third party modules.
import six

# Local modules.
from pyxray.meta.reference import Reference

# Globals and constants variables.

@six.add_metaclass(abc.ABCMeta)
class _Parser(object):
    """
    (abstract) Class to parse X-ray related information from a data source.
    """

    def __init__(self, reference):
        """
        :arg reference: reference of the parsed source
        :type reference: :class:`Reference <pyxray.meta.reference.Reference>`
        """
        self._reference = reference

    @abc.abstractmethod
    def parse(self):
        """
        Returns :class:`list` of :class:`dict` where each dictionary is a 
        parsed entry. The keys of these dictionaries are defined by 
        :meth:`keys` and the values must be Python primitives (float, str, int). 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def keys(self):
        """
        Returns :class:`set` of parsed keys.
        """
        raise NotImplementedError

    @property
    def reference(self):
        return self._reference

class _CachedParser(_Parser):
    """
    (abstract) Special parser that caches the parsed data.
    """

    def __init__(self, reference, usecache=True):
        super().__init__(reference)
        self._usecache = usecache

    def _dump_cache(self, entries):
        json_filepath = self._get_cache_filepath()
        checksum_filepath = self._get_cache_checksum_filepath()

        data = {'entries': entries,
                'reference': self.reference.todict()}
        with open(json_filepath, 'w') as fp:
            json.dump(data, fp)

        checksum = self._calculate_checksum(json_filepath)
        with open(checksum_filepath, 'w') as fp:
            fp.write(checksum)

        logger.info('Entries cached at {0}'.format(json_filepath))

    def _load_cache(self):
        json_filepath = self._get_cache_filepath()
        checksum_filepath = self._get_cache_checksum_filepath()

        with open(checksum_filepath, 'r') as fp:
            expected_checksum = fp.read()
        actual_checksum = self._calculate_checksum(json_filepath)
        if expected_checksum != actual_checksum:
            raise IOError('Checksums do not match')

        with open(json_filepath, 'r') as fp:
            data = json.load(fp)

        reference = Reference(**data['reference'])
        if reference != self.reference:
            raise ValueError('Cached reference "{0}" does not match parser "{1}"'
                             .format(data.get('reference'), self.reference))

        return data.get('entries', [])

    def _calculate_checksum(self, filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _has_cache(self):
        return os.path.exists(self._get_cache_filepath())

    def _get_cache_filepath(self):
        dirpath = os.path.join(os.path.dirname(__file__), '..', 'data', 'cache')
        dirpath = os.path.abspath(dirpath)
        os.makedirs(dirpath, exist_ok=True)

        filename = '{0.__module__}.{0.__name__}'.format(self.__class__)
        filename = filename.replace('.', '_').lower()
        filename += '.json'
        return os.path.join(dirpath, filename)

    def _get_cache_checksum_filepath(self):
        return self._get_cache_filepath() + '.md5'

    def parse(self):
        if self._usecache and self._has_cache():
            try:
                entries = self._load_cache()
            except:
                logger.exception("Exception in reading cache")
            else:
                logger.info('Entries loaded from cache')
                return entries

        entries = self.parse_nocache()

        self._dump_cache(entries)

        return entries

    @abc.abstractmethod
    def parse_nocache(self):
        raise NotImplementedError


