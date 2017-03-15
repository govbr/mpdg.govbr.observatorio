#-*- coding: utf-8 -*-
import logging
from plone import api
from Products.contentmigration.archetypes import InplaceATFolderMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from StringIO import StringIO

from mpdg.govbr.observatorio.config import PROJECTNAME


logger = logging.getLogger(PROJECTNAME)


class BoaPraticaBaseMigrator(InplaceATFolderMigrator):
    walkerClass = CatalogWalker
    src_portal_type = 'BoaPratica'
    src_meta_type = 'BoaPratica'
    dst_portal_type = 'BoaPratica'
    dst_meta_type = 'BoaPratica'

    def custom(self):
        self.new.setCreationDate(self.old.created())
        self.new.reindexObject()


def upgrade_boapratica(context):
    out = StringIO()
    print >> out, "Starting migration"

    portal = api.portal.get()
    migrators = (BoaPraticaBaseMigrator,)

    for migrator in migrators:
        walker = migrator.walkerClass(portal, migrator)
        walker.go(out=out)
        print >> out, walker.getOutput()

    print >> out, "Migration finished"
    import transaction; transaction.commit()
    logger.info(out.getvalue())
