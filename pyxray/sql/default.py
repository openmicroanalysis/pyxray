""""""

# Standard library modules.
import os
import argparse

# Third party modules.
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

# Local modules.
from pyxray.sql.model import \
    (Base, Reference,
     ElementSymbolProperty, ElementNameProperty, ElementAtomicWeightProperty,
     ElementMassDensityProperty)
from pyxray.sql.util import session_scope

# Globals and constants variables.

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

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

def populate_element_symbol_table(engine):
    with session_scope(engine) as session:
        ref = require_reference(session, 'unattributed')

        for z, symbol in enumerate(SYMBOLS, 1):
            p = ElementSymbolProperty(z=z, symbol=symbol, reference=ref)
            session.add(p)

        session.commit()

def main():
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description='Create sql database')
    parser.add_argument('-o', '--output', help='Output file path',
                        default=os.path.join(BASEDIR, '..', 'data', 'pyxray.sql'))

    args = parser.parse_args()

    outfilepath = os.path.abspath(args.output)
    engine = create_engine('sqlite:///' + outfilepath)
    print('Opened database: {0}'.format(outfilepath))

    create_tables(engine)
    print('Created tables')

    populate_element_symbol_table(engine)
    print('Populated symbol table')

if __name__ == '__main__':
    main()
