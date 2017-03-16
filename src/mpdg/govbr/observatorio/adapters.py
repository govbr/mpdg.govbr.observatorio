# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component import adapts

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.adapters.ofsfile import BlobbableOFSFile

from mpdg.govbr.observatorio.content.interfaces import IBoaPratica


class BlobbableBoaPratica(BlobbableOFSFile):
    """ adapter for ATFile objects to work with blobs """
    implements(IBlobbable)
    adapts(IBoaPratica)

    def filename(self):
        """ see interface ... """
        return self.context.getFilename()
