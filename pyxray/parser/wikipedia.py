""""""

# Standard library modules.

# Third party modules.
import requests

# Local modules.
from pyxray.meta.parser import _CachedParser
from pyxray.meta.reference import Reference

# Globals and constants variables.

class _WikipediaParser(_CachedParser):

    REFERENCE = Reference('wikipedia',
                          author='Wikipedia contributors',
                          publisher='Wikipedia, The Free Encyclopedia')

    def __init__(self, usecache=True):
        super().__init__(self.REFERENCE, usecache)

class WikipediaElementNameParser(_WikipediaParser):

    KEY_Z = 'z'
    KEY_LANGUAGE_CODE = 'lang'
    KEY_NAME = 'name'

    NAMES_EN = [
        "Hydrogen"    , "Helium"      , "Lithium"     , "Beryllium"   ,
        "Boron"       , "Carbon"      , "Nitrogen"    , "Oxygen"      ,
        "Fluorine"    , "Neon"        , "Sodium"      , "Magnesium"   ,
        "Aluminium"   , "Silicon"     , "Phosphorus"  , "Sulfur"      ,
        "Chlorine"    , "Argon"       , "Potassium"   , "Calcium"     ,
        "Scandium"    , "Titanium"    , "Vanadium"    , "Chromium"    ,
        "Manganese"   , "Iron"        , "Cobalt"      , "Nickel"      ,
        "Copper"      , "Zinc"        , "Gallium"     , "Germanium"   ,
        "Arsenic"     , "Selenium"    , "Bromine"     , "Krypton"     ,
        "Rubidium"    , "Strontium"   , "Yttrium"     , "Zirconium"   ,
        "Niobium"     , "Molybdenum"  , "Technetium"  , "Ruthenium"   ,
        "Rhodium"     , "Palladium"   , "Silver"      , "Cadmium"     ,
        "Indium"      , "Tin"         , "Antimony"    , "Tellurium"   ,
        "Iodine"      , "Xenon"       , "Cesium"      , "Barium"      ,
        "Lanthanum"   , "Cerium"      , "Praseodymium", "Neodymium"   ,
        "Promethium"  , "Samarium"    , "Europium"    , "Gadolinium"  ,
        "Terbium"     , "Dysprosium"  , "Holmium"     , "Erbium"      ,
        "Thulium"     , "Ytterbium"   , "Lutetium"    , "Hafnium"     ,
        "Tantalum"    , "Tungsten"    , "Rhenium"     , "Osmium"      ,
        "Iridium"     , "Platinum"    , "Gold"        , "Mercury"     ,
        "Thallium"    , "Lead"        , "Bismuth"     , "Polonium"    ,
        "Astatine"    , "Radon"       , "Francium"    , "Radium"      ,
        "Actinium"    , "Thorium"     , "Protactinium", "Uranium"     ,
        "Neptunium"   , "Plutonium"   , "Americium"   , "Curium"      ,
        "Berkelium"   , "Californium" , "Einsteinium" , "Fermium"     ,
        "Mendelevium" , "Nobelium"    , "Lawrencium"  , "Rutherfordium",
        "Dubnium"     , "Seaborgium"  , "Bohrium"     , "Hassium"     ,
        "Meitnerium"  , "Darmstadtium", "Roentgenium" , "Copernicium" ,
        "Ununtrium"   , "Flerovium"   , "Ununpentium" , "Livermorium" ,
        "Ununseptium" , "Ununoctium"
    ]

    # 30 most spoken languages in the world
    # https://en.wikipedia.org/wiki/List_of_languages_by_number_of_native_speakers
    LANGUAGES = ['cmn', 'es', 'en', 'hi', 'ar', 'pt', 'bn', 'ru', 'ja', 'pa',
                 'de', 'jv', 'wuu', 'ms', 'te', 'vi', 'ko', 'fr', 'mr', 'ta',
                 'ur', 'tr', 'it', 'yue', 'th', 'gu', 'cjy', 'nan', 'fa', 'pl']

    def _find_wikipedia_names(self, name_en):
        """
        Finds all Wikipedia pages referring to the specified name in English and 
        returns a dictionary where the keys are the language code and the values
        are the titles of the corresponding pages.
        """
        url = 'https://en.wikipedia.org/w/api.php'
        data = {'action': 'query',
                'titles': name_en,
                'prop': 'langlinks',
                'lllimit': 500,
                'format': 'json'}
        r = requests.post(url, data=data)
        if not r:
            raise ValueError('Could not find wikipedia page: {0}'.format(name_en))
        out = r.json()

        names = {}
        pages = out['query']['pages']
        for page in pages:
            for langlink in pages[page].get('langlinks', []):
                names[langlink['lang']] = langlink['*']

        return names

    def parse_nocache(self):
        entries = []
        for z, name_en in enumerate(self.NAMES_EN, 1):
            entries.append({self.KEY_Z: z,
                            self.KEY_LANGUAGE_CODE: 'en',
                            self.KEY_NAME: name_en})


            names = self._find_wikipedia_names(name_en)
            for lang, name in names.items():
                if lang not in self.LANGUAGES: continue
                entries.append({self.KEY_Z: z,
                                self.KEY_LANGUAGE_CODE: lang,
                                self.KEY_NAME: name})

        return entries

    def keys(self):
        return set([self.KEY_Z, self.KEY_LANGUAGE_CODE, self.KEY_NAME])
