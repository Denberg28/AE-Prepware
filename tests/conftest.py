"""Never let collection of backend.api touch a developer's default study DB."""
import os
import tempfile


def pytest_configure(config):
    config._ae_previous_db = os.environ.get('AE_DB')
    config._ae_test_db = tempfile.TemporaryDirectory(prefix='ae-pytest-')
    os.environ['AE_DB'] = os.path.join(config._ae_test_db.name, 'collection.sqlite')


def pytest_unconfigure(config):
    previous = getattr(config, '_ae_previous_db', None)
    if previous is None:
        os.environ.pop('AE_DB', None)
    else:
        os.environ['AE_DB'] = previous
    if hasattr(config, '_ae_test_db'):
        config._ae_test_db.cleanup()
