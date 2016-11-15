"""
Parsers from data collected from Wikipedia.
"""

# Standard library modules.
import os
import logging
logger = logging.getLogger(__name__)

# Third party modules.
import requests

try:
    import requests_cache
    dirpath = os.path.join(os.path.dirname(__file__), '..', 'data', 'cache')
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, 'wikipedia')
    requests_cache.install_cache(filepath)
except ImportError:
    pass

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, Element, Language
from pyxray.property import ElementName

# Globals and constants variables.

WIKIPEDIA = Reference('wikipedia',
                      author='Wikipedia contributors')

class WikipediaElementNameParser(_Parser):

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
        params = {'action': 'query',
                  'titles': name_en,
                  'prop': 'langlinks',
                  'lllimit': 500,
                  'format': 'json'}
        r = requests.get(url, params=params)
        if not r:
            raise ValueError('Could not find wikipedia page: {0}'.format(name_en))
        out = r.json()

        names = {}
        pages = out['query']['pages']
        for page in pages:
            for langlink in pages[page].get('langlinks', []):
                names[langlink['lang']] = langlink['*']

        return names

    def __iter__(self):
        length = len(self.NAMES_EN)
        for z, name_en in enumerate(self.NAMES_EN, 1):
            element = Element(z)
            language = Language('en')
            prop = ElementName(WIKIPEDIA, element, language, name_en)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

            names = self._find_wikipedia_names(name_en)
            for code, name in names.items():
                if code not in self.LANGUAGES: continue
                language = Language(code)
                prop = ElementName(WIKIPEDIA, element, language, name)
                logger.debug('Parsed: {0}'.format(prop))
                yield prop

            self.update(int((z - 1) / length * 100.0))
