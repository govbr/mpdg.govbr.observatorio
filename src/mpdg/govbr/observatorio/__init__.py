# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

from Products.Archetypes import atapi
from Products.CMFCore.utils import ContentInit

from mpdg.govbr.observatorio import config

MessageFactory = MessageFactory('mpdg.govbr.observatorio')

def initialize(context):
    """Inicializador chamado quando usado como um produto Zope 2."""

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        ContentInit(
            '%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types=(atype, ),
            permission=config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors=(constructor,),).initialize(context)
