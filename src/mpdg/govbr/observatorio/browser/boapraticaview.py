# -*- coding: utf-8 -*-
import logging
import datetime
from five import grok
from plone import api
from plone.app.caching.operations.utils import doNotCache
from plone.uuid.interfaces import IUUID
from z3c.caching.purge import Purge
from zope.component import getUtility
from zope.event import notify
from zope.schema.interfaces import IVocabularyFactory
from zope.security import checkPermission
from plone.directives import form
from z3c.form import button
from zope import schema
from zope.component import getUtility

from mpdg.govbr.observatorio.browser.utils import sizeof_fmt
from mpdg.govbr.biblioteca.content.arquivo_biblioteca import ArquivoBiblioteca
from mpdg.govbr.observatorio.content.interfaces import IBoaPratica
from mpdg.govbr.observatorio.browser.utils import ContadorManager
from mpdg.govbr.observatorio.config import PROJECTNAME
from Products.statusmessages.interfaces import IStatusMessage
from plone.registry.interfaces import IRegistry


FILE_CONTENT_TYPES = ArquivoBiblioteca.dict_file_content_types


logger = logging.getLogger(PROJECTNAME)


grok.templatedir('templates')


class ICommentPraticaView(form.Schema):
    nome     = schema.TextLine(title=u"Nome", required=True )
    email    = schema.TextLine(title=u"E-mail", required=True)
    comentario = schema.Text(title=u"Comentário", required=True)


class BoaPraticaView(form.SchemaForm):
    grok.context(IBoaPratica)
    grok.require('zope2.View')
    grok.name('boapratica-view')

    schema = ICommentPraticaView
    ignoreContext = True

    def update(self):
        self.request.set('disable_border',1)
        return super(BoaPraticaView, self).update()

    @button.buttonAndHandler(u'Comentar')
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

            


        #TODO: Exibir mensagem que o comentario foi enviado para aprovação
        messages = IStatusMessage(self.request)
        messages.add(u"Obrigado. Seu comentário foi enviado para aprovação.", type=u"info")
        
        nome     = data['nome']
        email    = data['email']
        comentario = data['comentario']

        

        criar_comentario= api.content.create(
            type = 'Comentario',
            nome = nome,
            email = email,
            created=datetime.datetime.now(),
            title = '{0} - {1}'.format(nome, email),
            comentario = comentario,
            container= self.context
             )
      
        return self.request.response.redirect(self.context.absolute_url())

    def get_ip(self, request):
        """
        Extract the client IP address from the HTTP request in proxy compatible way.

        @return: IP address as a string or None if not available
        """
        if "HTTP_X_FORWARDED_FOR" in request.environ:
            # Virtual host
            ip = request.environ["HTTP_X_FORWARDED_FOR"]
        elif "HTTP_HOST" in request.environ:
            # Non-virtualhost
            ip = request.environ["REMOTE_ADDR"]
        else:
            # Unit test code?
            ip = None

        return ip

    def getAccessObject(self):
        uid = self.context.UID()
        content_type = self.context.meta_type
        contador = ContadorManager(uid=uid, content_type=content_type)
        return contador.setAcesso()

    def getFilesRelated(self):
        """ Metodo retorna os arquivos bibliotecas relacionados a boa pratica """
        rc = api.portal.get_tool('reference_catalog')
        results = rc.searchResults(
            relationship='uid_pratica',
            targetUID=self.context.UID()
        )
        uids_arquivos = []
        for ref in results:
            ref_obj = ref.getObject()
            uids_arquivos.append(ref_obj.sourceUID)
        catalog = api.portal.get_tool(name='portal_catalog')
        files = catalog.searchResults(
            portal_type='ArquivoBiblioteca',
            UID=uids_arquivos
        )

        data = []
        for file in files:
            data_file = file.getObject()
            full_ctype = data_file.getContentType()
            ctype = 'NONE'
            for type in FILE_CONTENT_TYPES:
                if full_ctype in FILE_CONTENT_TYPES[type]:
                    ctype = type
                    break

            data.append({
                         'title'  : data_file.Title(),
                         'UID'    : data_file.UID,
                         'ctype'  : ctype,
                         'status' : file.review_state,
                         'url'    : data_file.absolute_url(),
                         'created': data_file.created().strftime('%d/%m/%Y'),
                         'size'   : sizeof_fmt(data_file.size())})

        return data

    def getCategoria(self):
        categoria = self.context.getCategoria()
        if categoria:
            factory = getUtility(IVocabularyFactory, 'mpdg.govbr.observatorio.CategoriasBoaPratica')
            vocab   = factory(self)
            try:
                term = vocab.getTerm(categoria)
                return term.title
            except LookupError:
                return None

     

    


#   Verificar se o usuario tem permissão de Modificar o conteúdo do portal
    def user_has_permission(self):
        if api.user.is_anonymous():
            return False

        pm = api.portal.get_tool('portal_membership')
        username    = pm.getAuthenticatedMember().getUserName()
        permissions = api.user.get_permissions(username)

        # permissions = getSecurityManager().checkPermission(permissions.ModifyPortalContent, username)
        if permissions.get('Modify portal content'):
        # if permissions:
            return True
        return False

    # Verificar se o usuario e dono ou tem permissao do conteúdo do portal

    def is_owner(self):
        """returns True if current user is owner of context's object"""
        user = api.user.get_current()
        owner = self.context.getOwner()
        if user.id == owner.getId():
            return True
        return False

    def getSitesRelacionados(self):
        sites_relacionados = self.context.getSitesrelacionados()
        results = []

        for site in sites_relacionados:
            url = site['url']

            if url:
                if url.find('http') == -1:
                    url = 'http://' + url

            results.append({
                'description': site['description'],
                'url': url
                }
            )

        return results

    def getComentarios(self):
            catalog_comment = api.portal.get_tool('portal_catalog')
            path = '/'.join(self.context.getPhysicalPath())
            busca = catalog_comment.searchResults(
                portal_type ='Comentario' ,
                review_state = 'published',
                path=path )

            results = []
            for item in busca:
                obj = item.getObject()
                created = obj.getCreated()
                results.append({
                    'name': obj.getNome(),
                    'email': obj.getEmail(),
                    'created': created.strftime('%d/%m/%y, %H:%M'),
                    'text': obj.getComentario(),

                })

            return results


    def canManageComments(self):
        return checkPermission('cmf.RequestReview', self.context)

    def getDataReplies(self):
        """
            Método retorna um dicionario com os dados dos comentários do conteúdo do contexto

            @return: Retorna o dicionario com os dados - qtd_replies - Quandidade de respostas no conteúdo
                                                         qtd_pending - Quantidade de respostas pendenetes
                                                         data - Lista de comentarios aprovados
        """
        approved = self.getComentarios()
        qtd_replies = len(approved)

        return {'qtd_replies': qtd_replies,
                'qtd_pending': len(self.getPendingComments()),
                'data': approved}

    def getPendingComments(self):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        brains = catalog.searchResults(
            portal_type = 'Comentario',
            review_state = 'pending',
            path = path)
        return brains


    