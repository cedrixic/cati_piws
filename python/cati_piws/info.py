version_major = 0
version_minor = 0
version_micro = 1
version_extra = 'alpha'

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
__version__ = '%s.%s.%s%s' % (version_major,
                              version_minor,
                              version_micro,
                              version_extra)
# Main setup parameters
NAME = 'cati_piws'
DESCRIPTION = 'CATI external data exposition'
PROJECT = 'cati_piws'
ORGANISATION = 'CATI'
AUTHOR = 'CATI'
AUTHOR_EMAIL = 'support@cati-neuroimaging.com'
URL = 'https://cati.cea.fr'
LICENSE = 'CeCILL-B'
VERSION = __version__
REQUIRES = ['catidb_api']
