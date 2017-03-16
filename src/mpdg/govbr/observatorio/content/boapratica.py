# -*- coding: utf-8 -*-
# from AccessControl import ClassSecurityInfo
from Products.Archetypes.utils import DisplayList
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata, folder
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from zope.component import getUtility
from zope.interface import implements
from plone.app.blob.field import FileField
from zope.schema.interfaces import IVocabularyFactory
from plone.app.folder.folder import ATFolder, ATFolderSchema
from mpdg.govbr.observatorio import MessageFactory as _
from mpdg.govbr.observatorio.config import PROJECTNAME
from mpdg.govbr.observatorio.content.interfaces import IBoaPratica


BoaPratica_schema = ATFolderSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='esfera',
        default=u'federal',
        widget=atapi.SelectionWidget(label=_(u"Essa prática é esfera"),),
        required=True,
        vocabulary='vocEsfera',
    ),

    atapi.StringField(
        name='uf',
        title=u'UF',
        widget=atapi.SelectionWidget(label=_(u"UF"),),
        required=False,
        vocabulary="vocBrasilEstados",
    ),

   atapi.StringField(
        name='orgparticipantes',
        widget=atapi.StringWidget(
            label=_(u"Órgãos participantes"),
        ),
        required=False,
    ),

    atapi.StringField(
        name='categoria',
        widget=atapi.SelectionWidget(label=_(u"Assunto"),),
        required=False,
        vocabulary='vocCategorias',
    ),

    DataGridField(
        name='sitesrelacionados',
        searchable = False,
        columns=("url", "description"),
        widget = DataGridWidget(
            label=_(u"Sites relacionados"),
            columns={
                'url' : Column("URL"),
                'description' : Column("Descrição da URL"),
            },
        ),
    ),

    # atapi.ReferenceField(
    #     name='anexos',
    #     widget = ReferenceBrowserWidget(
    #         label=_(u"Anexos"),
    #     ),
    #     type=['File', 'ArquivoBiblioteca'],
    #     required=True,
    #     multiValued=True,
    # )

    FileField(
        name='anexos',
        title=u'Anexo',
        description=u'É obrigatório a inserção de pelo menos um anexo',
        required=True,
    ),

))

BoaPratica_schema['description'].default_content_type = 'text/html'
BoaPratica_schema['description'].allowable_content_types = ('text/html', )
BoaPratica_schema['description'].default_output_type = 'text/html'
BoaPratica_schema['description'].widget = atapi.RichWidget(
    label=u'Descrição',
    allow_file_upload=False
)

schemata.finalizeATCTSchema(BoaPratica_schema, folderish=True)

class BoaPratica(folder.ATFolder):
    """ Reserve Content for BoaPratica"""

    implements(IBoaPratica)

    portal_type = 'BoaPratica'

    schema = BoaPratica_schema

    _at_rename_after_creation = True

    def vocEsfera(self):
        return DisplayList(((u'federal', u'Federal'),
                            (u'estadual', u'Estadual'),
                            (u'municipal', u'Municipal')))
    def vocAtuacao(self):
        return DisplayList(((u'cidadao', u'Cidadão'),
                            (u'gestao', u'Gestão'),
                            (u'integracao', u'Integração')))
    def vocOrgParticipantes(self):
        return DisplayList(((u'', u'-- Selecione --'),))


    def vocCategorias(self):
        factory = getUtility(IVocabularyFactory, 'mpdg.govbr.observatorio.CategoriasBoaPratica')
        terms = factory(self)._terms
        dl = []
        for term in terms:
            dl.append((term.value, term.title))
        return tuple(dl)

    def vocBrasilEstados(self):
        factory = getUtility(IVocabularyFactory, 'brasil.estados')
        terms = factory(self)._terms
        dl = [(u'', u'-- Selecione --')]
        for term in terms:
            dl.append((term.value, term.title))
        return tuple(dl)


atapi.registerType(BoaPratica, PROJECTNAME)
