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
    (Reference,
     Element, ElementNameProperty, ElementAtomicWeightProperty,
     ElementMassDensityProperty, NotationType,
     AtomicShell, AtomicShellNotationProperty)
from pyxray.sql.util import session_scope

# Globals and constants variables.

def setup_table(engine, model_class, purge=False):
    """
    Setups a table defined by the *model_class*.
    If *purge*, the existing table in the database is dropped if it exists.
    If *purge* is ``False`` and the table already exists in the database, the
    function returns ``False``, indicating that nothing should be done.
    Otherwise, a new table is created.
    
    :return: :class:`True` if the table should be populated, ``False`` otherwise
    :rtype: :class:`bool`
    """
    table = model_class.__table__

    if purge:
        table.drop(engine, checkfirst=True)

    if table.exists(engine):
        return False

    table.create(engine)
    return True

def require_reference(session, bibtexkey, **kwargs):
    """
    Returns a reference with the specified *bibtexkey*.
    If it does not exists, if is created with the specified keyword-arguments.
    
    :rtype: :class:`Reference <pyxray.sql.model.Reference>`
    """
    try:
        return session.query(Reference).\
                    filter(Reference.bibtexkey == bibtexkey).one()
    except NoResultFound:
        ref = Reference(bibtexkey=bibtexkey, **kwargs)
        session.add(ref)
        session.commit()
        return ref

def require_notation(session, name):
    """
    Returns an :class:`NotationType <pyxray.sql.model.NotationType>`.
    
    :arg name: name of notation
    
    :rtype: :class:`NotationType <pyxray.sql.model.NotationType>`
    """
    return session.query(NotationType).filter(NotationType.name == name).one()

def require_element(session, z):
    """
    Returns an :class:`Element <pyxray.sql.model.Element>`.
    
    :arg z: atomic number
    
    :rtype: :class:`Element <pyxray.sql.model.Element>`
    """
    return session.query(Element).filter(Element.z == z).one()

def require_shell(session, n):
    """
    Returns an :class:`AtomicShell <pyxray.sql.model.AtomicShell>`.
    
    :arg n: primary quantum number
    
    :rtype: :class:`AtomicShell <pyxray.sql.model.AtomicShell>`
    """
    return session.query(AtomicShell).filter(AtomicShell.n == n).one()

#--- Helper

def populate_reference_table(engine, purge=False):
    if not setup_table(engine, Reference, purge):
        return False

    with session_scope(engine) as session:
        ref = Reference(bibtexkey='unattributed')
        session.add(ref)
        session.commit()

    return True

def populate_notation_type_table(engine, purge=False):
    if not setup_table(engine, NotationType, purge):
        return False

    with session_scope(engine) as session:
        ref_unattributed = require_reference(session, 'unattributed')

        n = NotationType(name='Siegbahn', reference=ref_unattributed)
        session.add(n)

        n = NotationType(name='Atomic', reference=ref_unattributed)
        session.add(n)

        ref_iupac = \
            require_reference(session, 'jenkins1991',
                              author='Jenkins, R. and Manne, R. and Robin, R. and Senemaud, C.',
                              year='1991',
                              pages='149--155',
                              journal='X-Ray Spectrometry',
                              title='{IUPAC} --- nomenclature system for x-ray spectroscopy',
                              volume='20')
        n = NotationType(name='IUPAC', reference=ref_iupac)
        session.add(n)

        session.commit()

    return True

#--- Element

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

def populate_element_table(engine, purge=False):
    if not setup_table(engine, Element, purge):
        return False

    with session_scope(engine) as session:
        for z, symbol in enumerate(SYMBOLS, 1):
            element = Element(z=z, symbol=symbol)
            session.add(element)

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

def populate_element_name_table(engine, purge=False):
    if not setup_table(engine, ElementNameProperty, purge):
        return False

    with session_scope(engine) as session:
        ref = require_reference(session, 'wikipedia2016',
                                author='Wikipedia',
                                year=2016)

        for z, name_en in enumerate(NAMES_EN, 1):
            element = require_element(session, z)

            prop = ElementNameProperty(element=element, name=name_en,
                                       language_code='en', reference=ref)
            session.add(prop)

            for lang, name in _find_wikipedia_names(name_en).items():
                prop = ElementNameProperty(element=element, name=name,
                                           language_code=lang, reference=ref)
                session.add(prop)

            logger.debug('Processed {0}'.format(name_en))

        session.commit()

    return True

#--- Atomic shell

def populate_atomic_shell_table(engine, purge=False):
    if not setup_table(engine, AtomicShell, purge):
        return False

    with session_scope(engine) as session:
        for n in range(1, 7 + 1):
            s = AtomicShell(principal_quantum_number=n)
            session.add(s)
        session.commit()

    return True

SHELL_NOTATION = ['K', 'L', 'M', 'N', 'O', 'P', 'Q']

def populate_atomic_shell_notation_table(engine, purge=False):
    if not setup_table(engine, AtomicShellNotationProperty, purge):
        return False

    with session_scope(engine) as session:
        notation_types = [require_notation(session, 'iupac'),
                          require_notation(session, 'siegbahn'), ]

        for n, notation in enumerate(SHELL_NOTATION, 1):
            shell = require_shell(session, n)

            for notation_type in notation_types:
                p = AtomicShellNotationProperty(atomic_shell=shell,
                                                value=notation,
                                                value_html=notation,
                                                value_latex=notation,
                                                notation_type=notation_type)
                session.add(p)

        session.commit()

    return True

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

    populates = [('reference', populate_reference_table),
                 ('notation type', populate_notation_type_table),
                 ('element', populate_element_table),
#                 ('element name', populate_element_name_table),
                 ('atomic subshell', populate_atomic_shell_table),
                 ('atomic subshell notation', populate_atomic_shell_notation_table),
                 ]

    for name, func in populates:
        if func(engine, purge):
            logger.info('Populated {0} table'.format(name))
        else:
            logger.info('Skipped {0} table'.format(name))

if __name__ == '__main__':
    main()
