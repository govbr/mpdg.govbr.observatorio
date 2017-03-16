# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from AccessControl import Unauthorized


grok.templatedir('templates')


class DeletarArquivoBiblioteca(grok.View):
    grok.name('deletar_arq_biblioteca')
    grok.require('zope2.View')
    grok.context(Interface)

    def update(self):
        uids    = self.request.form.get('uids')
        catalog = api.portal.get_tool('portal_catalog')
        brains  = catalog.searchResults(UID=uids)
        if brains:
            idanexo = brains[0].getObject()

            username = api.user.get_current().id
            permissions = api.user.get_permissions(username)

            if idanexo.Creator() == username or permissions.get('Modify portal content'):
                api.content.delete(obj = idanexo)
            else:
                raise Unauthorized('Você não tem permissão para executar essa ação.')

        self.message('Arquivo deletado com sucesso!')
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
