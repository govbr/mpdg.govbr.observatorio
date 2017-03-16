# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api


class RemoveObservatorioFolder(BrowserView):
    def __call__(self):
        portal = api.portal.get()
        sobre = portal['sobre']
        sobre._delObject('copy_of_observatorio', suppress_events=True)
        import transaction; transaction.commit()
        return 'folder deleted'


class ClearBoasPraticas(BrowserView):
    def __call__(self):
        portal = api.portal.get()
        praticas = portal['sobre']['observatorio']['boas-praticas']
        for pratica in praticas.keys():
            praticas._delObject(pratica, suppress_events=True)
        import transaction; transaction.commit()
        return 'folder cleared'
