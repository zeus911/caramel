#! /usr/bin/env python
# vim: expandtab shiftwidth=4 softtabstop=4 tabstop=17 filetype=python :

# Make things as three-ish as possible (requires python >= 2.6)
from __future__ import (unicode_literals, print_function,
                        absolute_import, division)
#
# ----- End header -----
#

import os
import sys

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    init_session,
    SubjectAltName,
    SubjectAltNameKinds,
    CSR,
)
import transaction

# Namespace cleanup
del unicode_literals, print_function, absolute_import, division


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def generateSAN():
    """Upgrade feature by adding an expected field to the DB"""
    csrs = CSR.all()
    for csr in csrs:
        if not csr.x509_sans:
            with transaction.manager:
                san = SubjectAltName(SubjectAltNameKinds.DNS, csr.commonname)
                csr.x509_sans.append(san)
                san.save()


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    init_session(engine, create=True)
    generateSAN()
