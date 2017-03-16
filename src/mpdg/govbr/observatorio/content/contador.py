# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.ATContentTypes.content.base import ATContentTypeSchema, ATCTContent

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata

from mpdg.govbr.observatorio.content.interfaces import IContador
from DateTime.DateTime import DateTime
from mpdg.govbr.observatorio.config import PROJECTNAME
from mpdg.govbr.observatorio import MessageFactory as _

ContadorSchema = ATContentTypeSchema.copy() + atapi.Schema((

    # contador
    atapi.IntegerField(
        name = 'contador',
        required =True,
        default = 0,
    ),

    # content_type
    atapi.StringField(
        name = 'content_type',
        required = True,
    ),

    # uid
    atapi.StringField(
        name='uid_obj',
        required=True,
    ),
))

schemata.finalizeATCTSchema(ContadorSchema)

class Contador(ATCTContent):
    """ Classe do conteudo Contardor
    """

    implements(IContador)

    meta_type = "Contador"
    schema = ContadorSchema
   
atapi.registerType(Contador, PROJECTNAME)
