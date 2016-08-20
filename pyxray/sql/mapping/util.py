""""""

# Standard library modules.

# Third party modules.
from sqlalchemy.orm.exc import NoResultFound

# Local modules.
from pyxray.meta.reference import Reference as ReferenceObj
from pyxray.sql.model import \
    (Reference, NotationType,
     Element, AtomicShell, AtomicSubshell)

# Globals and constants variables.

def get_key(key):
    def funckey(session, entry):
        return entry[key]
    return funckey

def get_reference(key_reference):
    def funckey(session, entry):
        reference = ReferenceObj(**entry[key_reference])
        query = session.query(Reference)
        query = query.filter(Reference.bibtexkey == reference.bibtexkey)
        try:
            return query.one()
        except NoResultFound:
            ref = Reference(**reference.todict())
            session.add(ref)
            session.commit()
            return funckey(session, entry)
    return funckey

def get_notation_type(key_notation):
    def funckey(session, entry):
        name = entry[key_notation]
        query = session.query(NotationType)
        query = query.filter(NotationType.name == name)
        return query.one()
    return funckey

def get_element(key_z):
    def funckey(session, entry):
        z = entry[key_z]
        query = session.query(Element)
        query = query.filter(Element.z == z)
        return query.one()
    return funckey

def get_atomic_shell(key_n):
    def funckey(session, entry):
        n = entry[key_n]
        query = session.query(AtomicShell)
        query = query.filter(AtomicShell.n == n)
        return query.one()
    return funckey

def get_atomic_subshell(key_n, key_l, key_jn):
    def funckey(session, entry):
        atomic_shell = get_atomic_shell(key_n)(session, entry)
        l = entry[key_l]
        j_n = entry[key_jn]
        query = session.query(AtomicSubshell)
        query = query.filter(AtomicSubshell.atomic_shell == atomic_shell)
        query = query.filter(AtomicSubshell.l == l)
        query = query.filter(AtomicSubshell.j_n == j_n)
        return query.one()
    return funckey

#def get_transition(key_n0, key_l0, key_j0n,
#                   key_n1, key_l1, key_j1n,
#                   key_n2=None, key_l2=None, key_j2n=None):
#    def funckey(session, entry):
#        atomic_shell = get_atomic_shell(key_n)(session, entry)
#        l = entry[key_l]
#        j_n = entry[key_jn]
#        query = session.query(AtomicSubshell)
#        query = query.filter(AtomicSubshell.atomic_shell == atomic_shell)
#        query = query.filter(AtomicSubshell.l == l)
#        query = query.filter(AtomicSubshell.j_n == j_n)
#        return query.one()
#    return funckey
