""""""

# Standard library modules.
from contextlib import contextmanager

# Third party modules.
from sqlalchemy.orm import sessionmaker

# Local modules.

# Globals and constants variables.

@contextmanager
def session_scope(engine):
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker(bind=engine)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def one_or_list(values):
    if len(values) == 1:
        return values[0]
    else:
        values

