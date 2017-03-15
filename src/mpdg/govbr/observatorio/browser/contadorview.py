# -*- coding: utf-8 -*-
import logging

from five import grok
from plone import api
from zope.interface import Interface
from mpdg.govbr.observatorio.browser.utils import ContadorManager


grok.templatedir('templates')

class ContadorView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('contador-view')

    def update(self):
        """
        Essa view recebe uma url com as seguintes variáveis:
        /@@contador-view?uid=ajkldfhlakjsfh&ct=BoaPratica
        A view incrementa mais um no contador quando recebe as variaveis 'uid' e 'ct'
        E retorna apenas a quantidade atual quando recebe apenas a variável 'uid'
        """
        uid = self.request.form.get('uid')
        content_type = self.request.form.get('ct')

        contador = ContadorManager(uid, content_type)
        if uid and content_type:
            self.resultado = contador.setAcesso()
        elif uid:
            self.resultado = contador.getAcesso()
        else:
            return self.request.response.redirect('/')

        return super(ContadorView, self).update()
