# -*- coding: utf-8 -*-
from plone import api
from five import grok
import json
from mpdg.govbr.observatorio.mailer import simple_send_mail
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.CMFCore.interfaces import IActionSucceededEvent
from mpdg.govbr.observatorio.content.interfaces import IComentario
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


def send_email_after_approvation(context, event):
    wf = api.portal.get_tool('portal_workflow')
    history = wf.getHistoryOf('simple_publication_workflow', context)
    status = history[-1]
    if status['review_state'] == 'published':
        nome_do_usuario = context.Creator()
        usuario = api.user.get(username=nome_do_usuario)
        email = usuario.getProperty('email')
        portal_site = api.portal.get()
        titulo_do_site = portal_site.getProperty('title_2')
        descricao_do_site = context.Description()
        url_da_pratica =context.absolute_url()
        url_fale ="/fale-conosco/@@fale-conosco"
        url_do_site = api.portal.get().absolute_url()
        nome_pratica = context.Title()

        send_email_users(nome_pratica,descricao_do_site,url_da_pratica,
            url_do_site + url_fale,email,titulo_do_site)

#enviar email para usuario quando a prática for aprovada
def send_email_users(nome_pratica,description ,url_da_pratica,url_do_site,email,title):
    """enviar um email para o admin"""

    message ="""A prática: %s foi aprovada
                Descrição: %s
                Link de visualização da prática: %s
                Em caso de dúvidas, entre em contato através do endereço: %s""" %(nome_pratica, description,
                                                                                 url_da_pratica,url_do_site)

    address ='%s' % (email)
    subject ='Sua Prática no %s foi aprovada' %(title)

    return simple_send_mail(message,address,subject)

def get_pratica_url(context):
    pratica = context.aq_parent
    return pratica.absolute_url()


def notify_admin_new_comment(context, event):
    """notifica o administrador do observatorio que ha novo comentario pendente de aprovacao"""
    url_aprovacao = '{0}/@@manage-comments-view'.format(get_pratica_url(context))

    message = """Há um novo Comentário pendente para análise de aprovação. \n
    clique no link para visualizar o comentário.\n
     %s """ %(url_aprovacao)

    registry = getUtility(IRegistry)
    address = registry.records['mpdg.govbr.observatorio.controlpanel.IObservatorio_email.adm_observatorio'].value
    subject = 'Novo comentário pendente na prática %s' %(context.Title())

    return simple_send_mail(message,address,subject)


@grok.subscribe(IComentario, IActionSucceededEvent)
def notify_user_comment_published(context, event):
    """notifica o usuario que seu comentario foi publicado"""
    if event.action == 'publish':
        url_da_pratica = get_pratica_url(context)
        message = """Seu comentário foi aprovado

                            link para visualizar  prática %s""" %(url_da_pratica)

        address = context.getEmail()

        subject = 'Seu comentário foi aprovado'

        return simple_send_mail(message,address,subject)


# @grok.subscribe(IComentario, IObjectRemovedEvent)
# def notify_user_comment_rejected(context, event):
#     """notifica o usuario que seu comentario foi rejeitado"""
#     url_da_pratica = get_pratica_url(context)

#     message = """Seu comentário foi rejeitado pois fere as políticas de uso do sítio/Política de Privacidade

#                         link para visualizar  prática %s""" %(url_da_pratica)
#     address = context.getEmail()
#     subject='seu comentário foi rejeitado'


#     return simple_send_mail(message,address,subject)




