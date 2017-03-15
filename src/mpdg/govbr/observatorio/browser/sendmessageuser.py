# -*- coding: utf-8 -*-
from five import grok
from mpdg.govbr.observatorio.mailer import simple_send_mail
from plone import api
from plone.autoform import directives
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from zope import schema
from zope.interface import Interface

grok.templatedir('templates')


class ISendMessageUserView(form.Schema):

    directives.mode(uids="hidden")
    uids = schema.TextLine(
        title=u"UIDS",
        required=True
    )

    directives.widget(mensagem='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    mensagem = schema.Text(
        title=u'Mensagem',
        required=True
    )


@form.default_value(field=ISendMessageUserView['uids'])
def default_uids(data):
    return data.request.get('uids')


class SendMessageUserView(form.SchemaForm):
    grok.context(Interface)
    grok.name('send_message_user')
    grok.require('cmf.ModifyPortalContent')

    schema = ISendMessageUserView
    ignoreContext = True
    label = u"Notificar usuário"

    def update(self):
        uids = self.request.form.get('form.widgets.uids') or \
               self.request.form.get('uids')

        if not uids:
            return self._back_to_review_page(u'Você não pode acessar essa página diretamente')

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(UID=uids)

        if brains:
            obj = brains[0].getObject()
            creator = obj.Creator()
            user = api.user.get(creator)
            self.email = user.getProperty('email')
            self.pratice = {
                'title': obj.Title(),
                'description': obj.Description()
            }

        else:
            return self._back_to_review_page(u'Não foi encontrado uma prática com esse UID')

        return super(SendMessageUserView, self).update()

    @button.buttonAndHandler(u'Enviar')
    def handleApply(self, action):

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        title_mail = 'Notificação sobre a prática: {0}'.format(self.pratice['title'])
        simple_send_mail(data['mensagem'], self.email, title_mail)
        return self._back_to_review_page(u'Notificação enviada com sucesso')

    @button.buttonAndHandler(u'Cancelar')
    def handleCancel(self, action):
        return self._back_to_review_page(u'Mensagem descartada')

    def _back_to_review_page(self, message=None):
        if message:
            messages = IStatusMessage(self.request)
            messages.add(message, type='info')

        portal_url  = api.portal.get().absolute_url()
        target = '{0}/@@pratica-pendentes'.format(portal_url)
        return self.request.response.redirect(target)
