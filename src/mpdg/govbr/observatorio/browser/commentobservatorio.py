# -*- coding: utf-8 -*-
from plone.directives import form
from mpdg.govbr.observatorio.content.interfaces import IBoaPratica
from five import grok
from plone import api
from zope import schema
from plone.autoform import directives
from Products.CMFCore.interfaces import ISiteRoot
from z3c.form import button
from Products.CMFCore.utils import getToolByName

grok.templatedir('templates')


class ICommentMensagemView(form.Schema):
    nome     = schema.TextLine(title=u"Nome", required=True )
    email    = schema.TextLine(title=u"E-mail", required=True)
    comentario = schema.Text(title=u"Comentário", required=True)


class CommentMensagemView(form.SchemaForm):
    grok.name('comentario')
    grok.require('zope2.View')
    grok.context(IBoaPratica)

    schema = ICommentMensagemView
    ignoreContext = False

    label = u"Comentar o conteudo"



    @button.buttonAndHandler(u'Comentar')
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return


        nome     = data['nome']
        email    = data['email']
        comentario = data['comentario']

        

        criar_comentario= api.content.create(
            type = 'Comentario',
            nome = nome,
            email = email, 
            title = '{0} - {1}'.format(nome, email),
            comentario = comentario,
            container= self.context
             )
      
        return self.request.response.redirect(self.context.absolute_url())
            