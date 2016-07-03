""""""

# Standard library modules.
import os
import argparse
import logging
logger = logging.getLogger(__name__)

# Third party modules.
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

import requests

# Local modules.
from pyxray.sql.model import \
    (Base, Reference,
     ElementSymbolProperty, ElementNameProperty, ElementAtomicWeightProperty,
     ElementMassDensityProperty)
from pyxray.sql.util import session_scope

# Globals and constants variables.

def setup_table(engine, model_class, purge=False):
    table = model_class.__table__

    if purge:
        table.drop(engine, checkfirst=True)

    if table.exists(engine):
        return False

    table.create(engine, checkfirst=True)
    return True

def require_reference(session, bibtexkey, **kwargs):
    try:
        return session.query(Reference).\
                    filter(Reference.bibtexkey == bibtexkey).one()
    except NoResultFound:
        ref = Reference(bibtexkey=bibtexkey, **kwargs)
        session.add(ref)
        session.commit()
        return ref

SYMBOLS = [
        "H"  , "He" , "Li" , "Be" , "B"  , "C"  , "N"  , "O",
        "F"  , "Ne" , "Na" , "Mg" , "Al" , "Si" , "P"  , "S",
        "Cl" , "Ar" , "K"  , "Ca" , "Sc" , "Ti" , "V"  , "Cr",
        "Mn" , "Fe" , "Co" , "Ni" , "Cu" , "Zn" , "Ga" , "Ge",
        "As" , "Se" , "Br" , "Kr" , "Rb" , "Sr" , "Y"  , "Zr",
        "Nb" , "Mo" , "Tc" , "Ru" , "Rh" , "Pd" , "Ag" , "Cd",
        "In" , "Sn" , "Sb" , "Te" , "I"  , "Xe" , "Cs" , "Ba",
        "La" , "Ce" , "Pr" , "Nd" , "Pm" , "Sm" , "Eu" , "Gd",
        "Tb" , "Dy" , "Ho" , "Er" , "Tm" , "Yb" , "Lu" , "Hf",
        "Ta" , "W"  , "Re" , "Os" , "Ir" , "Pt" , "Au" , "Hg",
        "Tl" , "Pb" , "Bi" , "Po" , "At" , "Rn" , "Fr" , "Ra",
        "Ac" , "Th" , "Pa" , "U"  , "Np" , "Pu" , "Am" , "Cm",
        "Bk" , "Cf" , "Es" , "Fm" , "Md" , "No" , "Lr" , "Rf",
        "Db" , "Sg" , "Bh" , "Hs" , "Mt" , "Ds" , "Rg" , "Cn",
        "Uut", "Fl" , "Uup", "Lv" , "Uus", "Uuo"
    ]

def populate_element_symbol_table(engine, purge=False):
    if not setup_table(engine, ElementSymbolProperty, purge):
        return False

    with session_scope(engine) as session:
        ref = require_reference(session, 'unattributed')

        for z, symbol in enumerate(SYMBOLS, 1):
            p = ElementSymbolProperty(z=z, symbol=symbol, reference=ref)
            session.add(p)

        session.commit()

    return True

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

def _find_wikipedia_names(name_en):
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

def populate_element_name(engine, purge=False):
    if not setup_table(engine, ElementNameProperty, purge):
        return False

    with session_scope(engine) as session:
        ref = require_reference(session, 'wikipedia2016',
                                author='Wikipedia',
                                year=2016)

        for z, name_en in enumerate(NAMES_EN, 1):
            p = ElementNameProperty(z=z, name=name_en,
                                    language_code='en', reference=ref)
            session.add(p)

            for lang, name in _find_wikipedia_names(name_en).items():
                p = ElementNameProperty(z=z, name=name,
                                        language_code=lang, reference=ref)
                session.add(p)

            logger.debug('Processed {0}'.format(name_en))

        session.commit()

def main():
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description='Create sql database')
    parser.add_argument('-o', '--output', help='Output file path',
                        default=os.path.join(BASEDIR, '..', 'data', 'pyxray.sql'))
    parser.add_argument('--purge', action='store_true',
                        help='Purge existing table(s)')

    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    args = parser.parse_args()
    outfilepath = os.path.abspath(args.output)
    purge = args.purge

    engine = create_engine('sqlite:///' + outfilepath)
    logger.info('Opened database: {0}'.format(outfilepath))

    if populate_element_symbol_table(engine, purge):
        logger.info('Populated element symbol table')
    else:
        logger.info('Skipped element symbol table')

    if populate_element_name(engine, purge):
        logger.info('Populated element name table')
    else:
        logger.info('Skipped element name table')

if __name__ == '__main__':
    main()
