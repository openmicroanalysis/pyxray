""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.sql.mapping.mapper import SqlMapper
from pyxray.sql.mapping.util import \
    (get_key, get_reference, get_notation_type,
     get_atomic_shell, get_atomic_subshell)
from pyxray.sql.model import \
    (NotationType,
     Element,
     AtomicShell, AtomicShellNotationProperty,
     AtomicSubshell, AtomicSubshellNotationProperty)
from pyxray.parser.base import \
    (NotationTypeParser,
     ElementParser,
     AtomicShellParser, AtomicShellNotationParser,
     AtomicSubshellParser, AtomicSubshellNotationParser)

# Globals and constants variables.

model = NotationType
parser = NotationTypeParser()
bindings = {NotationType.name: get_key(parser.KEY_NAME),
            NotationType.reference: get_reference(parser.KEY_REFERENCE)}
mapper_notation_type = SqlMapper(model, parser, bindings)

model = Element
parser = ElementParser()
bindings = {Element.z: get_key(parser.KEY_Z),
            Element.symbol: get_key(parser.KEY_SYMBOL)}
mapper_element = SqlMapper(model, parser, bindings)

model = AtomicShell
parser = AtomicShellParser()
bindings = {AtomicShell.n: get_key(parser.KEY_N)}
mapper_atomic_shell = SqlMapper(model, parser, bindings)

model = AtomicShellNotationProperty
parser = AtomicShellNotationParser()
bindings = {AtomicShellNotationProperty.atomic_shell: get_atomic_shell(parser.KEY_N),
            AtomicShellNotationProperty.notation_type: get_notation_type(parser.KEY_NOTATION),
            AtomicShellNotationProperty.value: get_key(parser.KEY_VALUE),
            AtomicShellNotationProperty.value_html: get_key(parser.KEY_VALUE_HTML),
            AtomicShellNotationProperty.value_latex: get_key(parser.KEY_VALUE_LATEX)}
mapper_atomic_shell_notation = SqlMapper(model, parser, bindings, [mapper_atomic_shell, mapper_notation_type])

model = AtomicSubshell
parser = AtomicSubshellParser()
bindings = {AtomicSubshell.atomic_shell: get_atomic_shell(parser.KEY_N),
            AtomicSubshell.l: get_key(parser.KEY_L),
            AtomicSubshell.j_n: get_key(parser.KEY_Jn)}
mapper_atomic_subshell = SqlMapper(model, parser, bindings, [mapper_atomic_shell])

model = AtomicSubshellNotationProperty
parser = AtomicSubshellNotationParser()
bindings = {AtomicSubshellNotationProperty.atomic_subshell: \
                get_atomic_subshell(parser.KEY_N, parser.KEY_L, parser.KEY_Jn),
            AtomicSubshellNotationProperty.notation_type: get_notation_type(parser.KEY_NOTATION),
            AtomicSubshellNotationProperty.value: get_key(parser.KEY_VALUE),
            AtomicSubshellNotationProperty.value_html: get_key(parser.KEY_VALUE_HTML),
            AtomicSubshellNotationProperty.value_latex: get_key(parser.KEY_VALUE_LATEX)}
mapper_atomic_subshell_notation = SqlMapper(model, parser, bindings, [mapper_atomic_subshell])
