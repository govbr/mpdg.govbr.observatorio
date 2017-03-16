# -*- coding: utf-8 -*-
from zope import schema
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from plone.z3cform import layout
from plone.directives import form
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper


class IObservatorio_email(form.Schema):

    adm_observatorio = schema.TextLine(
        title = u'email administrador do observatorio',
        description = u'irforme o email administrador do observatorio',
        required = True, 
        default = u'catia.parreira@planejamento.gov.br',
    )


class ObservatorioSettings(RegistryEditForm):
    """
    """
    schema = IObservatorio_email
    label = u"Configurações Observatorio"



class SettingsView(grok.View):
    """
    """
    grok.name("observatorio-adm")
    grok.context(ISiteRoot)



    def render(self):
        view_factor = layout.wrap_form(ObservatorioSettings, ControlPanelFormWrapper)
        view = view_factor(self.context, self.request)
        return view()
