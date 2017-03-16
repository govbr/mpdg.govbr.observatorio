# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from AccessControl import Unauthorized
from mpdg.govbr.observatorio.mailer import simple_send_mail


grok.templatedir('templates')


class DeletarComentario(grok.View):
    grok.name('deletar_comentario')
    grok.require('cmf.ModifyPortalContent')
    grok.context(Interface)

    def update(self):
        uids    = self.request.form.get('uids')
        catalog = api.portal.get_tool('portal_catalog')
        brains  = catalog.searchResults(UID=uids)
        if brains:
            obj = brains[0].getObject()
            self.notify_user_comment_rejected(obj)
            api.content.delete(obj=obj)
            return self._back_to(obj.aq_parent, 'Comentário deletado com sucesso!')
        else:
            return self._back_to(self.context.aq_parent, 'Não foi encontrado um comentário com esse UID')

    def _back_to(self, context, message=None):

        target = context.absolute_url()+'/@@manage-comments-view'

        if message:
            messages = IStatusMessage(self.request)
            messages.add(message, type='info')

        return self.request.response.redirect(target)

    def message(self, mensagem):
        messages = IStatusMessage(self.request)
        messages.add(mensagem, type='info')
        return

    def notify_user_comment_rejected(self, comment):
        """notifica o usuario que seu comentario foi rejeitado"""
        url_da_pratica = comment.aq_parent.absolute_url()
        message = """Seu comentário foi rejeitado pois fere as políticas de uso do sítio/Política de Privacidade

                            link para visualizar  prática %s""" %(url_da_pratica)
        address = comment.getEmail()
        subject='seu comentário foi rejeitado'

        return simple_send_mail(message,address,subject)
