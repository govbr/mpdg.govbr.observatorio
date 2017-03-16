# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.statusmessages.interfaces import IStatusMessage
from plone import api


grok.templatedir('templates')


class PublicarArquivoBiblioteca(grok.View):
    grok.name('publicar_arq_biblioteca')
    grok.require('cmf.ModifyPortalContent')
    grok.context(Interface)

    def update(self):

        uids    = self.request.form.get('uids')
        catalog = api.portal.get_tool('portal_catalog')
        brains  = catalog.searchResults(UID=uids)
        if brains:
            obj = brains[0].getObject()
            api.content.transition(obj=obj, transition='publish')
            #new_state = api.content.get_state(obj=obj)
            
        self.message('Arquivo publicado com sucesso!')
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