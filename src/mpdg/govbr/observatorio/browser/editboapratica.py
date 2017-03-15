# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from plone.i18n.normalizer import idnormalizer
from plone.namedfile.field import NamedFile
from plone import api
from z3c.form import button
from plone.autoform import directives
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from z3c.form import field
from z3c.form import error
from zope import schema
from zope import interface
from zope.component import getUtility
from zope.component import provideAdapter
from zope.interface import Interface
from mpdg.govbr.biblioteca.content.arquivo_biblioteca import ArquivoBiblioteca
from plone.registry.interfaces import IRegistry
from zope.schema.interfaces import IVocabularyFactory
from mpdg.govbr.observatorio.browser.utils import sizeof_fmt, fix_sitesrelacionados_dict
from mpdg.govbr.observatorio.content.interfaces import IBoaPratica
from Products.statusmessages.interfaces import IStatusMessage


FILE_CONTENT_TYPES = ArquivoBiblioteca.dict_file_content_types

grok.templatedir('templates')


class ITableRowEditSchema(interface.Interface):
    url = schema.TextLine(
        title=u"URL",
        required=False)
    description = schema.TextLine(
        title=u"Descrição",
        required=False)


class IBoaPraticaEditForm(form.Schema):

    title = schema.TextLine(
        title=u"Título",
        required=False,)

    directives.widget(esfera='z3c.form.browser.radio.RadioFieldWidget')
    esfera = schema.Choice(
        title=u"Essa prática é esfera",
        required=False,
        vocabulary="mpdg.govbr.observatorio.EsferaPratica")

    uf = schema.Choice(
        title=u"UF",
        description=u"Selecione o seu Estado.",
        required=False,
        vocabulary="brasil.estados",)

    orgparticipantes = schema.TextLine(
        title=u"Órgãos participantes",
        description=u"Se a prática estiver relacionada a algum órgão de governo, favor informar no campo abaixo",
        required=False,
        )

    directives.widget(description='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    description = schema.Text(
        title=u"Descrição",
        required=False)

    directives.widget(sitesrelacionados='collective.z3cform.datagridfield.DataGridFieldFactory')
    sitesrelacionados = schema.List(
        title=u"Sites relacionados",
        value_type=DictRow(
            title=u"tablerow",
            schema=ITableRowEditSchema),
        required=False)

    # anexo = NamedFile(
    #     title=u"Anexo",
    #     description=u'É obrigatório a inclusão de pelo menos um anexo.',
    #     required=True)



@form.default_value(field=IBoaPraticaEditForm['title'])
def default_name(data):
    #import pdb; pdb.set_trace()
    return data.context.Title()
@form.default_value(field=IBoaPraticaEditForm['esfera'])
def default_esfera(data):
    return data.context.esfera
@form.default_value(field=IBoaPraticaEditForm['orgparticipantes'])
def default_orgparticipantes(data):
    return data.context.orgparticipantes
@form.default_value(field=IBoaPraticaEditForm['description'])
def default_description(data):
    return data.context.Description()
@form.default_value(field=IBoaPraticaEditForm['sitesrelacionados'])
def default_sitesrelacionados(data):
    return data.context.sitesrelacionados



class EditBoaPratica(form.SchemaForm):
    """docstring for ClassName"""

    grok.name('editar-boa-pratica')
    grok.require('zope2.View')
    grok.context(IBoaPratica)

    ignoreContext = True
    schema = IBoaPraticaEditForm

    def update(self):
        self.request.set('disable_border', True)
        # TODO: verificar se o usuário é dono da boapratica para acessar essa view
        return super(EditBoaPratica, self).update()

    def viewEditarBoaPratica(self):
        return None

    @button.buttonAndHandler(u"Voltar")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        return self._back_to()

    @button.buttonAndHandler(u'Enviar')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.context.setTitle(data['title'])
        self.context.setEsfera(data['esfera'])
        self.context.setOrgparticipantes(data['orgparticipantes'])
        self.context.setDescription(data['description'])

        sitesrelacionados = fix_sitesrelacionados_dict(data['sitesrelacionados'])
        self.context.setSitesrelacionados(sitesrelacionados)

        import transaction
        transaction.commit()

        self.message('Boa prática editada com sucesso!')
        return self._back_to()


    def _back_to(self, message=None):

        observatorio = self.context.absolute_url()

        if message:
            messages = IStatusMessage(self.request)
            messages.add(message, type='info')

        return self.request.response.redirect(observatorio)

    def message(self, mensagem):
        messages = IStatusMessage(self.request)
        messages.add(mensagem, type='info')
        return
