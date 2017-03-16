# -*- coding: utf-8 -*-

from five import grok

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.component import queryUtility
from zope.interface import implements
from plone.i18n.normalizer import idnormalizer

from Products.CMFCore.utils import getToolByName

class EsferaPratica(object):
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        return SimpleVocabulary([SimpleTerm(value='federal', title='Federal'),
                                 SimpleTerm(value='estadual', title='Estadual'),
                                 SimpleTerm(value='municipal', title='Municipal')])

grok.global_utility(EsferaPratica, name=u'mpdg.govbr.observatorio.EsferaPratica')

class EixoAtuacao(object):
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        return SimpleVocabulary([SimpleTerm(value='cidadao', title='Cidadão'),
                                 SimpleTerm(value='gestao', title='Gestão'),
                                 SimpleTerm(value='integracao', title='Integração')])

grok.global_utility(EixoAtuacao, name=u'mpdg.govbr.observatorio.EixoAtuacao')

class CategoriasBoaPratica(object):
    implements(IVocabularyFactory)
    
    def __call__(self, context=None):
        
        terms = self.vocab_vcge()
        assuntos_vcge = [{'value': term.title, 'title': term.title} for term in terms]
        assuntos_vcge.sort()
        vocab = []
        for assunto in assuntos_vcge:
            vocab.append(
                SimpleTerm(value=idnormalizer.normalize(assunto['value'], max_length=200), title=assunto['title'])
            )
        return SimpleVocabulary(vocab)

    def vocab_vcge(self):
        name = 'brasil.gov.vcge'
        util = queryUtility(IVocabularyFactory, name)
        vcge = util(self)
        return vcge

        
grok.global_utility(CategoriasBoaPratica, name=u'mpdg.govbr.observatorio.CategoriasBoaPratica')
