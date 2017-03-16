# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import (getSecurityManager,
                                              newSecurityManager,
                                              setSecurityManager)
from collective.documentviewer.async import queueJob
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from collective.z3cform.keywordwidget.field import Keywords
from collective.z3cform.keywordwidget.widget import KeywordFieldWidget
from five import grok
from plone import api
from plone.autoform import directives
from plone.directives import form
from plone.i18n.normalizer import idnormalizer
from plone.namedfile.field import NamedFile
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button, error, field
from z3c.form.browser.radio import RadioFieldWidget
from zope import interface, schema
from zope.component import getUtility, provideAdapter
from zope.interface import Interface
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.schema.interfaces import IVocabularyFactory

from mpdg.govbr.observatorio.browser.utils import ProcessFiles, sizeof_fmt, fix_sitesrelacionados_dict
from mpdg.govbr.biblioteca.content.arquivo_biblioteca import ArquivoBiblioteca
from mpdg.govbr.observatorio.content.interfaces import IBoaPratica
from mpdg.govbr.observatorio.mailer import simple_send_mail

FILE_CONTENT_TYPES = ArquivoBiblioteca.dict_file_content_types

grok.templatedir('templates')


class ITableRowSchema(interface.Interface):
    url = schema.TextLine(
        title=u"URL",
        required=False)
    description = schema.TextLine(
        title=u"Descrição",
        required=False)


class IBoaPraticaForm(form.Schema):

    title = schema.TextLine(
        title=u"Título",
        required=True,)

    directives.widget(esfera='z3c.form.browser.radio.RadioFieldWidget')
    esfera = schema.Choice(
        title=u"Essa prática é esfera",
        required=True,
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

    # categoria = schema.Choice(
    #     title=u"Assunto",
    #     vocabulary="liberiun.govcontent.CategoriasBoaPratica")

    directives.widget(description='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    description = schema.Text(
        title=u"Descrição",
        required=False,
    )

    # Subject = Keywords(
    #     title=u'Tags',
    #     required=False,)

    directives.widget(sitesrelacionados='collective.z3cform.datagridfield.DataGridFieldFactory')
    sitesrelacionados = schema.List(
        title=u"Sites relacionados",
        value_type=DictRow(
            title=u"tablerow",
            schema=ITableRowSchema),
        required=False)

    anexo = NamedFile(
        title=u"Anexo",
        description=u'É obrigatório a inclusão de pelo menos um anexo.',
        required=True)


class NovaBoaPratica(ProcessFiles, form.SchemaForm):
    label=u"Inscrição de Boas Práticas"

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('nova-boa-pratica')

    ignoreContext = True
    # enableCSRFProtection = True

    schema = IBoaPraticaForm

    # fields = field.Fields(IBoaPraticaForm)
    # fields['sitesrelacionados'].widgetFactory = DataGridFieldFactory
    # # fields['Subject'].widgetFactory = KeywordFieldWidget <- ignorar
    # fields['esfera'].widgetFactory = RadioFieldWidget

    def update(self):
        #Cria toda a hieraquia das Boas Praticas
        self.createBoaPraticaStructure()
        self.request.set('disable_border', True)
        return super(NovaBoaPratica, self).update()

    @button.buttonAndHandler(u"Voltar")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """


    @button.buttonAndHandler(u'Enviar')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # if action.form.widgets.errors:
        #     self.status = self.formErrorsMessage
        #     return
        if data['anexo'].contentType == 'application/msword' or data['anexo'].contentType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            messages = IStatusMessage(self.request)
            messages.add(u"Não é permitido efetuar o upload de arquivos Word.", type=u"error")
            return self.request.response.redirect(self.request.getURL())

        context = self.context

        # tool para criacao do conteudo
        # pt = getToolByName(context, 'portal_types')

        folder_observatorio = getattr(context, 'observatorio', None)
        folder_boas_praticas = getattr(folder_observatorio,  'boas-praticas', None)

        title = data['title']
        esfera = data['esfera']
        uf = data['uf']
        orgparticipantes = data['orgparticipantes']
        description = data['description']
        # Subject = data['Subject']
        sitesrelacionados = data['sitesrelacionados']
        # categoria = data['categoria']

        id = self.generateIdForContext(folder_boas_praticas, idnormalizer.normalize(title))
        boapratica = self.createObjectInContext(id, folder_boas_praticas, 'BoaPratica')
        boapratica.setTitle(title)
        boapratica.setEsfera(esfera)
        boapratica.setUf(uf)
        boapratica.setOrgparticipantes(orgparticipantes)
        boapratica.setDescription(description)
        # boapratica.setCategoria(categoria)

        # if Subject:
        #     boapratica.setSubject(Subject)

        sitesrelacionados = [site for site in sitesrelacionados if isinstance(site, dict) and site.get('url', None)]
        sitesrelacionados = fix_sitesrelacionados_dict(sitesrelacionados)
        boapratica.setSitesrelacionados(sitesrelacionados)

        anexo_obj = data.get('anexo', None)

        if anexo_obj:
            file = data["anexo"]
            # folder_attach = getattr(folder_boas_praticas, 'anexo-de-praticas')
            anexo_obj = self.processFiles(file, boapratica)

        if anexo_obj:
            boapratica.setAnexos((anexo_obj))

        boapratica.reindexObject()

        pw = getToolByName(context, "portal_workflow")
        try:
            pw.doActionFor(boapratica, "submit")
            pw.doActionFor(anexo_obj, "submit")
        except WorkflowException:
            #Não foi possivel enviar para revisão
            pass

        # if self.session.get("termo_aceito", False):
        #     del self.session['termo_aceito']
        # import pdb; pdb.set_trace()

        portal_site = api.portal.get()
        site_name = portal_site.getProperty('title_2')
        self.send_email_admin(boapratica.absolute_url(),site_name)

        messages = IStatusMessage(self.request)
        messages.add(u"Obrigado, sua boa prática foi enviada para aprovação.", type=u"info")

        self.request.response.redirect(boapratica.absolute_url())

    def send_email_admin(self, link ,title):
        """enviar um email para o admin"""

        message ="""Há uma nova prática para análise de aprovação. \n
        clique no link para visualizar a boa prática \n
        %s """ % (link)

        address = self.get_adm_observatorio()
        subject ='Existe nova prática pendente de avaliação no Observatório do %s ' % (title)

        return simple_send_mail(message,address,subject)

    def get_adm_observatorio(self):
        # Pega o usuário administrador do fale conosco.
        registry = getUtility(IRegistry)
        adm_observatorio = registry.records['mpdg.govbr.observatorio.controlpanel.IObservatorio_email.adm_observatorio'].value
        return adm_observatorio


    # traz o texto do termo de uso
    ### Obs :  O metodo foi comentado , descomentei pois não tinha acesso no boa pratica.
    def getTermo(self):
        portal = api.portal.get()
        sobre = getattr(portal, 'sobre')
        observatorio = getattr(sobre,'observatorio')
        termo = getattr(observatorio, 'termo-de-uso', None)

        return termo

    def createBoaPraticaStructure(self):
        """
        Cria toda a arquitetura das boas praticas:

        Pasta - Observatorio
          Página - Termo de Uso
          Pasta - Praticas
            Pasta - Anexos das Boas Praticas
        """

        portal_membership = getToolByName(self.context, "portal_membership")
        user_admin = portal_membership.getMemberById('admin')

        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()

        # create a new context, as the owner of the folder
        newSecurityManager(self.request,user_admin)

        folder_observatorio = getattr(self.context, 'observatorio', False)
        if not folder_observatorio:
            folder_observatorio = self.createObjectInContext('observatorio', self.context, 'Folder')
            folder_observatorio.setTitle('Observatório')
            try:
                self.context.portal_workflow.doActionFor(folder_observatorio, 'publish')
            except WorkflowException:
                pass

        if folder_observatorio:
            folder_boas_praticas = getattr(folder_observatorio,  'boas-praticas', False)
            document_termo_uso = getattr(folder_observatorio,  'termo-de-uso', False)

            if not folder_boas_praticas:
                folder_boas_praticas = self.createObjectInContext('boas-praticas', folder_observatorio, 'Folder')
                folder_boas_praticas.setTitle('Boas Práticas')
                try:
                    folder_observatorio.portal_workflow.doActionFor(folder_boas_praticas, 'publish')
                except WorkflowException:
                    pass

            if not document_termo_uso:
                document_termo_uso = self.createObjectInContext('termo-de-uso', folder_observatorio, 'Document')
                document_termo_uso.setTitle('Termo de Uso')
                try:
                    folder_observatorio.portal_workflow.doActionFor(document_termo_uso, 'publish')
                except WorkflowException:
                    pass

        # Legado. Removido na história 30718, sprint 5 (Out/16)
        # if folder_boas_praticas:
        #     folder_attach = getattr(folder_boas_praticas, 'anexo-de-praticas', False)

        #     if not folder_attach:
        #         folder_attach = self.createObjectInContext('anexo-de-praticas', folder_boas_praticas, 'Folder')
        #         folder_attach.setTitle('Anexo de Práticas')
        #         folder_attach.reindexObject()
        #         try:
        #             folder_boas_praticas.portal_workflow.doActionFor(folder_attach, 'publish')
        #         except WorkflowException:
        #             pass

        # restore the original context
        setSecurityManager(old_security_manager)

    def createObjectInContext(self, id, context, portal_type):
        """
            Cria uma pasta com o id passa em um contexto definido

            @param id: Id do conteúdo a ser criado
            @param context: Contexto onde será criado o conteúdo
            @param portal_type: Tipo de conteúdo que será criado

            @return: Objeto plone criado
        """
        portal = getUtility(ISiteRoot)
        ptypes = getToolByName(portal, 'portal_types')

        new_content = ptypes.getTypeInfo(portal_type)
        new_content = new_content._constructInstance(context, id)
        new_content.reindexObject()

        return new_content


    # TODO: manual translation of error messages...
    RequiredMissingErrorMessage = error.ErrorViewMessage(u'Esse campo é obrigatório', error=RequiredMissing)
    provideAdapter(RequiredMissingErrorMessage, name='message')

    @form.error_message(field=IBoaPraticaForm['anexo'], error=RequiredMissing)

    def anexoRequiredErrorMessage(value):
        return u'Campo Anexo é obrigatório. Favor inserir pelo menos um arquivo.'

    #Class que cuida do controle do Termo de Uso
