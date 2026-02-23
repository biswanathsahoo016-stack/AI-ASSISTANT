# bridge script, imports the real flask app from a package
# The bulk of the application logic lives in the ``app`` package so that
# Gunicorn invocations such as ``gunicorn app.py`` (which Render sometimes
# uses automatically) can still locate a WSGI callable by loading a submodule
# of the package named ``py``.

from app import application

if __name__ == '__main__':
    # forward the run call to the package; the package already knows how
    # to configure itself using environment variables.
    application.run(debug=True, host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 5000)))
