# This module exists solely to satisfy environments that incorrectly pass
# ``app.py`` as the WSGI application name to Gunicorn.  ``importlib`` will
# interpret the string "app.py" as a dotted name (package ``app`` and
# submodule ``py``), so by providing this file we allow those calls to succeed.
#
# When imported the file simply re‑exports the Flask application instance from
# the package's top level.

from . import application  # re-export module-level application variable
