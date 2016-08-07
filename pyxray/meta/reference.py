""""""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class Reference(object):

    __slots__ = ['_fields']

    def __init__(self, bibtexkey,
                 author=None,
                 year=None,
                 title=None,
                 type=None, #@ReservedAssignment
                 booktitle=None,
                 editor=None,
                 pages=None,
                 edition=None,
                 journal=None,
                 school=None,
                 address=None,
                 url=None,
                 note=None,
                 number=None,
                 series=None,
                 volume=None,
                 publisher=None,
                 organization=None,
                 chapter=None,
                 howpublished=None,
                 doi=None):
        self._fields = {}
        self._fields['bibtexkey'] = str(bibtexkey)
        self._fields['author'] = str(author)
        self._fields['year'] = str(year)
        self._fields['title'] = str(title)
        self._fields['type'] = str(type)
        self._fields['booktitle'] = str(booktitle)
        self._fields['pages'] = str(pages)
        self._fields['edition'] = str(edition)
        self._fields['journal'] = str(journal)
        self._fields['school'] = str(school)
        self._fields['address'] = str(address)
        self._fields['url'] = str(url)
        self._fields['note'] = str(note)
        self._fields['number'] = str(number)
        self._fields['series'] = str(series)
        self._fields['volume'] = str(volume)
        self._fields['publisher'] = str(publisher)
        self._fields['organization'] = str(organization)
        self._fields['chapter'] = str(chapter)
        self._fields['howpublished'] = str(howpublished)
        self._fields['doi'] = str(doi)

    def __getattr__(self, attr):
        if attr in self._fields:
            return self._fields[attr]
        raise AttributeError

    def __eq__(self, other):
        return self._fields == other._fields

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(frozenset(self._fields.items()))

    def todict(self):
        return self._fields.copy()

UNATTRIBUTED = Reference('unattributed')
