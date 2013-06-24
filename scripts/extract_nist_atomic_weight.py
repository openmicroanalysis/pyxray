"""
Extract atomic weights from NIST database.
The values are entered in the :class:`NISTElementPropertiesDatabase` class in 
the module :mod:`element_properties`
"""

import urllib2

url = 'http://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=&all=all&ascii=ascii2&isotype=some'

data = {}
for line in urllib2.urlopen(url):
    line = line.strip()

    if line.startswith("Atomic Number"):
        z = int(line.split('=')[1])
    elif line.startswith('Standard Atomic Weight'):
        weight = line.split('=')[1]
        weight = weight.translate(None, '()[]')
        weight = float(weight)

        data[z] = weight

print ', '.join(['%9f' % data[z] for z in sorted(data)])
