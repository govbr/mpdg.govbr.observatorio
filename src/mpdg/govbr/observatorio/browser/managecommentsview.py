# -*- coding: utf-8 -*-
from five import grok
from Products.CMFCore.utils import getToolByName
from plone import api
from DateTime import DateTime
from zope.interface import Interface
from mpdg.govbr.observatorio.content.interfaces import IBoaPratica

grok.templatedir('templates')

class managecommentsview(grok.View):
    # View responsavel por adiministração das mensagens boa praticas pendentes

    grok.context(IBoaPratica)
    grok.require("cmf.ModifyPortalContent")
    grok.name("manage-comments-view")

    def update(self):
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)
        return super(managecommentsview, self).update()

    def cmt_pendentes(self):

        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        brain   = catalog.searchResults(
            portal_type='Comentario',
            review_state='pending',
            sort_on='modified',
            path=path
        )

        comment = []
        for item in brain:
            obj = item.getObject()
            comment.append({
                'name': obj.getNome(),
                'email': obj.getEmail(),
                'text': obj.getComentario(),
                'url' : obj.absolute_url(),
                'uid': obj.UID()
            })

        return comment
