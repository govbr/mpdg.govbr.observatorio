# -*- coding: utf-8 -*-
import uuid
import zope.event
from five import grok
from z3c.form.action import ActionErrorOccurred
from z3c.form.interfaces import WidgetActionExecutionError
from zope.interface import Invalid, Interface
from collective.documentviewer.async import queueJob
from plone.i18n.normalizer import idnormalizer
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.contenttypes.content import Folder

from mpdg.govbr.biblioteca.content.arquivo_biblioteca import ArquivoBiblioteca
from mpdg.govbr.observatorio.content.contador import Contador

def fix_sitesrelacionados_dict(sitesrelacionados):
    """used to fix a bug on sitesrelacionados field at AT BoaPratica when
    description or url is None"""
    result = []
    for site in sitesrelacionados:
        item = site
        cond1 = site['description'] is None
        cond2 = site['url'] is None
        if cond1:
            item['description'] = ''
        if cond2:
            item['url'] = ''

        if cond1 or cond2:
            result.append(item)
        else:
            result.append(site)
    return result


def notifyWidgetActionExecutionError(action, widget, err_str):
    zope.event.notify(
        ActionErrorOccurred(
            action,
            WidgetActionExecutionError(widget, Invalid(err_str))
        )
    )

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


class ProcessFiles(object):
    def processFiles(self, data, folder, title=None):
        """
            Prepara os arquivos após o upload, adiciona um novo tipo ArquivoBiblioteca

            @param data: Arquivo tipo NamedFile
            @param folter: Objeto folder onde o arquivo será criado

            @return: retorna o objeto ArquivoBiblioteca criado
        """

        filename = data.filename
        blob = data.data
        ctype = data.contentType
        size = data.getSize()
        id = self.generateIdForContext(folder, idnormalizer.normalize(filename))

        pt = getToolByName(self.context, 'portal_types')
        type_info = pt.getTypeInfo('ArquivoBiblioteca')

        a_biblioteca = type_info._constructInstance(folder, id)

        a_biblioteca.setFile(blob)

        file = a_biblioteca.getFile()
        file.setContentType(ctype)
        file.setFilename(filename)

        titulo_arq = title or filename

        a_biblioteca.setContentType(ctype)
        a_biblioteca.setFilename(filename)
        a_biblioteca.setTitle(titulo_arq)
        a_biblioteca.setUid_pratica(folder)

        a_biblioteca.reindexObject()

        queueJob(a_biblioteca)
        return a_biblioteca

    def generateIdForContext(self, ctx, id, count=0):
        """
            Método que gera um id para um objeto dentro do contexto,
            caso o id já exista no contexto ele adiciona numero na frente

            @param ctx: Contexto para qual será gerado o Id
            @param id: O id do objeto
            @param count: Contador que vai a frente do id de entrada

            @return: valor de um id que não existe no contexto
        """

        if getattr(ctx, id, False):
            if count > 0:
                id = id[:(len(str(count))+1)*-1]
            count += 1
            id = '%s-%s' % (id, count)
            return self.generateIdForContext(ctx, id, count)
        else:
            return id


class UtilsView(grok.View):
    """
    View criada para concentrar métodos genericos da aplicação.
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('utils-view')


    def render(self):
        pass

    def getAccessObject(self, content_type):
        contador = ContadorManager(self.context.UID(), content_type)
        return contador.setAcesso()

    def getTags(self):
        if getattr(self.context, 'getRawSubject', False):
            return self.context.getRawSubject()
        else:
            return []

    def getFormatedTags(self):
        list_tags = self.getTags()
        str_tags = ''
        if list_tags:
            str_tags = ', '.join(list_tags)

        return str_tags

    def getRelatedContent(self):
        """
        Retorna um dicionário com os dados do objeto relacionado

        return (dict): Dicionario com os dados do objeto, o objeto deve ter o método _obj_to_dict para retornar os valores necessarios para a template.
        """

        if getattr(self.context, 'getRelatedItems', False):
            result = self.context.getRelatedItems()
            dict_obj = []
            for res in result:
                if getattr(res, '_obj_to_dict', False):
                    dict_obj.append(res._obj_to_dict())
            return dict_obj
        else:
            return []


class ContadorManager(object):
    def __init__(self, uid, content_type=None):
        self.uid = uid
        self.content_type = content_type

    def _create_folder(self):
        """Cria pasta 'contador-de-acessos' na raiz do portal se esta não existir
        criar e retornar True. Se a pasta já existir, retornar False.
        """
        portal = api.portal.get()
        if 'contador-de-acessos' not in portal:
            portal_types = api.portal.get_tool('portal_types')
            type_info = portal_types.getTypeInfo('Folder')
            content = type_info._constructInstance(
                portal,
                'contador-de-acessos',
                title='Contador de Acessos'
            )
            return content
        return

    def setAcesso(self):
        """
        :return: Quantidade de acessos de um objeto
        """
        catalog = api.portal.get_tool('portal_catalog')
        contador = catalog.unrestrictedSearchResults(
            portal_type='Contador',
            uid_obj=self.uid
        )

        if contador:
            obj = contador[0]._unrestrictedGetObject()
            valoratual = obj.getContador()
            obj.setContador(valoratual + 1)
            obj.reindexObject()
        else:
            portal = api.portal.get()
            if 'contador-de-acessos' not in portal:
                self._create_folder()

            objid = uuid.uuid4().get_hex()
            objtitle = '{0}-{1}'.format(self.content_type, self.uid)

            portal_types = api.portal.get_tool('portal_types')
            type_info = portal_types.getTypeInfo('Contador')
            target_folder = portal['contador-de-acessos']

            obj = type_info._constructInstance(
                target_folder,
                objid
            )
            obj.setTitle(objtitle)
            obj.setContador(1),
            obj.setContent_type(self.content_type)
            obj.setUid_obj(self.uid)
            obj.reindexObject()

        return obj.getContador()

    def getAcesso(self):
        """Retorna a quantidade de acessos de um objeto a partir do UID,"""
        catalog = api.portal.get_tool('portal_catalog')
        busca = catalog.unrestrictedSearchResults(
            portal_type ='Contador',
            uid_obj = self.uid,
        )
        qtdAcessos = 0
        if busca:
            obj = busca[0]._unrestrictedGetObject()
            qtdAcessos = obj.getContador()

        return qtdAcessos
