# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from mpdg.govbr.observatorio.content.interfaces import IComentario
from mpdg.govbr.observatorio.config import PROJECTNAME
from mpdg.govbr.observatorio import MessageFactory as _
from DateTime.DateTime import DateTime

ComentarioSchema = ATFolderSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='nome',
        required=True,
        widget=atapi.StringWidget(
            label=_(u"Nome"),
            description=_(u"")
        ),
    ),


    atapi.StringField(
        name='email',
        required=True,
        widget=atapi.StringWidget(
            label=_(u"E-mail"),
            description=_(u"")
        ),
    ),



    atapi.TextField(
        name='comentario',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(migrate=True),
        widget=atapi.TextAreaWidget(
            label=_(u"Comentário"),
            description=_(u""),
            rows=5,
       ),
    ),


    atapi.DateTimeField(
        name='created',
        required=0,
        searchable=1,
        default_method = 'getDefaultTime',
        widget = atapi.CalendarWidget(
            label = 'Date Added'
        ),
    )



))

        

schemata.finalizeATCTSchema(ComentarioSchema)

    

class Comentario(ATFolder):
    """ Classe do conteudo FaleConosco
    """

    implements(IComentario)

    meta_type = "Comentario"
    schema = ComentarioSchema

    _at_rename_after_creation = True

    def getDefaultTime (self): # função para retornar a data e hora atuais
     return DateTime () 

atapi.registerType(Comentario, PROJECTNAME)
