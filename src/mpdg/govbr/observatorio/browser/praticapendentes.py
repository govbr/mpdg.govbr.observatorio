# -*- coding: utf-8 -*-
from five import grok
from Products.CMFCore.utils import getToolByName
from plone import api
from DateTime import DateTime
from zope.interface import Interface


grok.templatedir('templates')

class PraticaPendentes(grok.View):
	# View responsavel por adiministração das mensagens boa praticas pendentes

    grok.context(Interface)
    grok.require("cmf.ModifyPortalContent")
    grok.name("pratica-pendentes")

    def update(self):
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)
        return super(PraticaPendentes, self).update()

    def msg_pendentes(self):

        catalog = api.portal.get_tool('portal_catalog')
        brain   = catalog.searchResults(
            portal_type  = 'BoaPratica',
            review_state  = 'pending',
            sort_on      = 'modified'
        )

        boapraticas = []
        for item in brain:
            obj = item.getObject()
            boapraticas.append({
                'UID'  : obj.UID,
                'titulo': obj.Title(),
                'descricao': obj.Description(),
                'pendente' : item.review_state,
                'url' : obj.absolute_url()
            })

        return boapraticas