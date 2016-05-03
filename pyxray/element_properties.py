"""
Various properties of atoms
"""

# Standard library modules.
from abc import ABCMeta, abstractmethod

# Third party modules.

# Local modules.

# Globals and constants variables.

class _ElementPropertiesDatabase(object):

    __metaclass__ = ABCMeta

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

    def symbol(self, z):
        """
        Returns the element's symbol.

        :arg z: atomic number
        """
        try:
            return self.SYMBOLS[z - 1]
        except IndexError:
            return ValueError, "Unknown atomic number: %i." % z

    def name(self, z):
        """
        Returns the element's name (in English).

        :arg z: atomic number
        """
        try:
            return self.NAMES_EN[z - 1]
        except IndexError:
            return ValueError, "Unknown atomic number: %i." % z

    def atomic_number(self, symbol=None, name=None):
        """
        Returns the atomic number for the specified symbol or element's name
        (in English).
        Either the symbol or the name must be specified.
        The symbol has precedence on the name if both are defined.
        This function is case insensitive.

        :arg symbol: symbol of the element (e.g. ``C``)
        :arg name: name of the element (e.g. ``carbon``)
        """
        if symbol is not None:
            try:
                return self.SYMBOLS.index(symbol.capitalize()) + 1
            except ValueError:
                raise ValueError("Unknown symbol: %s" % symbol)
        elif name is not None:
            try:
                return self.NAMES_EN.index(name.capitalize()) + 1
            except ValueError:
                raise ValueError("Unknown name: %s" % name)
        else:
            raise ValueError("Please specify a symbol or name")

    @abstractmethod
    def mass_density_kg_m3(self, z):
        """
        Returns the mass density (in kg/m3).

        :arg z: atomic number
        """
        raise NotImplementedError

    @abstractmethod
    def atomic_mass_kg_mol(self, z):
        """
        Returns the atomic mass (in kg/mol).

        :arg z: atomic number
        """
        raise NotImplementedError

class SargentWelchElementPropertiesDatabase(_ElementPropertiesDatabase):

    """
    Density and atomic mass values from Periodic Table of Elements,
    Sargent-Welch scientifique Canada Ltd.
    """

    DENSITIES = [
        0.0899, 0.1787, 0.5300, 1.8500, 2.3400, 2.6200, 1.2510, 1.4290,
        1.6960, 0.9010, 0.9700, 1.7400, 2.7000, 2.3300, 1.8200, 2.0700,
        3.1700, 1.7840, 0.8600, 1.5500, 3.0000, 4.5000, 5.8000, 7.1900,
        7.4300, 7.8600, 8.9000, 8.9000, 8.9600, 7.1400, 5.9100, 5.3200,
        5.7200, 4.8000, 3.1200, 3.7400, 1.5300, 2.6000, 4.5000, 6.4900,
        8.5500, 10.200, 11.500, 12.200, 12.400, 12.000, 10.500, 8.6500,
        7.3100, 7.3000, 6.6800, 6.2400, 4.9200, 5.8900, 1.8700, 3.5000,
        6.7000, 6.7800, 6.7700, 7.0000, 6.4750, 7.5400, 5.2600, 7.8900,
        8.2700, 8.5400, 8.8000, 9.0500, 9.3300, 6.9800, 9.8400, 13.100,
        16.600, 19.300, 21.000, 22.400, 22.500, 21.400, 19.300, 13.530,
        11.850, 11.400, 9.8000, 9.4000, None  , 9.9100, None  , 5.0000,
        10.070, 11.700, 15.400, 18.900, 20.400, 19.800, 13.600, 13.511
    ]

    ATOMIC_MASSES = [
        1.0079000, 4.0026000, 6.9410000, 9.0121800, 10.810000, 12.011000,
        14.006700, 15.999400, 18.998403, 20.179000, 22.989770, 24.305000,
        26.981540, 28.085500, 30.973760, 32.060000, 35.453000, 39.948000,
        39.098300, 40.080000, 44.955900, 47.900000, 50.941500, 51.996000,
        54.938000, 55.847000, 58.933200, 58.700000, 63.546000, 65.380000,
        69.720000, 72.590000, 74.921600, 78.960000, 79.904000, 83.800000,
        85.467800, 87.620000, 88.905600, 91.220000, 92.906400, 95.940000,
        98.000000, 101.07000, 102.90550, 106.40000, 107.86800, 112.41000,
        114.82000, 118.69000, 121.75000, 127.60000, 126.90450, 131.30000,
        132.90540, 137.33000, 138.90550, 140.12000, 140.90770, 144.24000,
        145.00000, 150.40000, 151.96000, 157.25000, 158.92540, 162.50000,
        164.93040, 167.26000, 168.93420, 173.04000, 174.96700, 178.49000,
        180.94790, 183.85000, 186.20700, 190.20000, 192.22000, 195.09000,
        196.96650, 200.59000, 204.37000, 207.20000, 208.98040, 209.00000,
        210.00000, 222.00000, 223.00000, 226.02540, 227.02780, 232.03810,
        231.03590, 238.02900, 237.04820, 244.00000, 243.00000, 247.00000,
        247.00000, 251.00000, 252.00000, 257.00000, 258.00000, 259.00000,
        260.00000, 261.00000, 262.00000, 263.00000
    ]

    def mass_density_kg_m3(self, z):
        if z == 85 or z == 87:
            raise ValueError("No mass density for atomic number: %i." % z)
        if z < 0 or z > 96:
            raise ValueError("No mass density for atomic number: %i." % z)

        try:
            return self.DENSITIES[z - 1] * 1000.0
        except IndexError:
            return ValueError("No mass density for atomic number: %i." % z)

    def atomic_mass_kg_mol(self, z):
        if z < 0 or z > 96:
            raise ValueError("No mass density for atomic number: %i." % z)

        try:
            return self.ATOMIC_MASSES[z - 1] / 1000.0
        except IndexError:
            return ValueError("No atomic mass for atomic number: %i." % z)

class NISTElementPropertiesDatabase(_ElementPropertiesDatabase):

    ATOMIC_MASSES = [
        1.007947, 4.002602, 6.941200, 9.012182, 10.811700, 12.010780,
        14.006720, 15.999430, 18.998403, 20.179760, 22.989769, 24.305060,
        26.981539, 28.085530, 30.973762, 32.065500, 35.453200, 39.948100,
        39.098310, 40.078400, 44.955913, 47.867100, 50.941510, 51.996160,
        54.938046, 55.845200, 58.933195, 58.693440, 63.546300, 65.382000,
        69.723100, 72.641000, 74.921602, 78.963000, 79.904100, 83.798200,
        85.467830, 87.621000, 88.905852, 91.224200, 92.906382, 95.962000,
        98.000000, 101.072000, 102.905502, 106.421000, 107.868220, 112.411800,
        114.818300, 118.710700, 121.760100, 127.603000, 126.904473, 131.293600,
        132.905452, 137.327700, 138.905477, 140.116100, 140.907652, 144.242300,
        145.000000, 150.362000, 151.964100, 157.253000, 158.925352, 162.500100,
        164.930322, 167.259300, 168.934212, 173.054500, 174.966810, 178.492000,
        180.947882, 183.841000, 186.207100, 190.233000, 192.217300, 195.084900,
        196.966569, 200.592000, 204.383320, 207.210000, 208.980401, 209.000000,
        210.000000, 222.000000, 223.000000, 226.000000, 227.000000, 232.038062,
        231.035882, 238.028913, 237.000000, 244.000000, 243.000000, 247.000000,
        247.000000, 251.000000, 252.000000, 257.000000, 258.000000, 259.000000,
        262.000000, 265.000000, 268.000000, 271.000000, 272.000000, 270.000000,
        276.000000, 281.000000, 280.000000, 285.000000, 284.000000, 289.000000,
        288.000000, 293.000000, 292.000000, 294.000000
        ]

# Utility functions at module level.
# Basically delegate everything to the instance element properties object.
#---------------------------------------------------------------------------

instance = SargentWelchElementPropertiesDatabase()

def get_instance():
    return instance

def set_instance(inst):
    global instance
    instance = inst

def symbol(z):
    """
    Returns the element's symbol.

    :arg z: atomic number
    """
    return instance.symbol(z)

def name(z):
    """
    Returns the element's name (in English).

    :arg z: atomic number
    """
    return instance.name(z)

def atomic_number(symbol=None, name=None):
    """
    Returns the atomic number for the specified symbol or element's name
    (in English).
    Either the symbol or the name must be specified.
    The symbol has precedence on the name if both are defined.
    This function is case insensitive.

    :arg symbol: symbol of the element (e.g. ``C``)
    :arg name: name of the element (e.g. ``carbon``)
    """
    return instance.atomic_number(symbol, name)

def mass_density_kg_m3(z):
    """
    Returns the mass density (in kg/m3).

    :arg z: atomic number (1-96)
    """
    return instance.mass_density_kg_m3(z)

def atomic_mass_kg_mol(z):
    """
    Returns the atomic mass (in kg/mol).

    :arg z: atomic number
    """
    return instance.atomic_mass_kg_mol(z)
