# -*- coding: utf-8 -*-
import hashlib

import pkg_resources
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from plone.directives import form
from plone.protect import CheckAuthenticator
from z3c.form import button
from zope import schema
from zope.component import getUtility
from zope.interface import Interface

from mpdg.govbr.observatorio.browser.utils import notifyWidgetActionExecutionError
from mpdg.govbr.observatorio.mailer import simple_send_mail


zope2_egg = pkg_resources.working_set.find(pkg_resources.Requirement.parse('Zope2'))
USE_SECURE_SEND = True
if zope2_egg and (zope2_egg.parsed_version >= pkg_resources.parse_version('2.12.3')):
    USE_SECURE_SEND = False

grok.templatedir('templates')

class IRegisterUserForm(form.Schema):
    
    name = schema.TextLine(
        title=u"Nome completo",
        description=u"Insira seu nome completo.", 
        required=True,)
    
    email = schema.TextLine(
        title=u"Email",
        description=u"Insira o seu email.",  
        required=True,)
    
    telefone = schema.TextLine(
        title=u"Telefone de contato",
        description=u"Insira seu telefone para contato.",  
        required=True,)
    
    uf = schema.Choice(
        title=u"UF", 
        description=u"Selecione o seu Estado.",
        required=True, 
        vocabulary="brasil.estados",)
    
    municipio = schema.TextLine(
        title=u"Município", 
        description=u"Selecione o seu município.",
        required=True,)
    
    password = schema.Password(
        title=u"Senha", 
        description=u"Insira sua senha de acesso ao portal.",
        required=True,)
    
    password_ctl = schema.Password(
        title=u"Confirme sua senha",
        description=u"Repita a senha inserida acima.", 
        required=True,)
    
class RegisterUserForm(form.SchemaForm):
    """ 
        Define Form handling

        This form can be accessed as http://yoursite/@@my-form
    """
    
    grok.name('create-new-user')
    grok.require('zope2.View')
    # grok.context(ISiteRoot)
    grok.context(Interface)
    
    
    schema = IRegisterUserForm
    ignoreContext = True
    enableCSRFProtection = True
    
    label = u"Cadastro"
    description = u"Cadastro de usuários"
    
    def __init__(self, context, request):
        form.SchemaForm.__init__(self, context, request)
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)

        self.back_to = session.get("back_to", self.context.absolute_url())

    @button.buttonAndHandler(u"Voltar")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""
        
        self.request.response.redirect(self.back_to)

    @button.buttonAndHandler(u'Continuar')
    def handleApply(self, action):
        data, errors = self.extractData()
        
        data['username'] = data.get('email', u'').encode('utf-8')
        self.validate_registration(action, data, errors)
        
        if action.form.widgets.errors:
            self.status = self.formErrorsMessage
            return
        
        context = self.context
        self.prepareMemberProperties()
        regtool = getToolByName(context, 'portal_registration')
        md5 = hashlib.md5()
        
        email = data.get('email').encode('utf-8')
        uuid = md5.update(email)
        uuid = md5.hexdigest()
        
        properties = {
            'username': email,
            'fullname': data.get('name'),
            'email': email,
            'telefone': data.get('telefone'),
            # 'orgaoresposavel': data.get('orgaoresposavel'),
            'uf': data.get('uf'),
            'municipio': data.get('municipio'),
            'uuid': uuid,
            'activate': False,
        }
        
        passwd = data.get('password')

        member = regtool.addMember(email, passwd, properties=properties)
        
        if member:
            self.sendActivationMail(member)
        
#         self.status = "Obrigado por se cadastrar"
        
        self.request.response.redirect(self.context.portal_url() + '/confirm-user-create')
        
    
    def sendActivationMail(self, member):
        uuid = member.getProperty('uuid')
        # portal = getUtility(ISiteRoot)
        
        message = """
                    Olá, %(name)s. \n
                    Recebemos sua solicitação de cadastro com o dado abaixo: \n
                    Login: %(login)s \n
                    Para continuar o seu cadastro clique no link abaixo: \n
                    <a href="%(activate_url)s"></a> \n
                    Se por algum motivo o link de confirmação não funcionar, você pode copiar todo o link de configuração e informá-lo em seu navegador de Internet. \n
                  """ % {'name': member.getProperty('fullname'),
                         'login': member.getId(),
                         'activate_url':  '%s/activate-account?u=%s&t=%s' % (self.context.portal_url(), member.getId(), uuid),}
        
        simple_send_mail(message, 
                         member.getProperty('email'), 
                         "Ativação da conta")

    def prepareMemberProperties(self):
        """ Adjust site for custom member properties """
        
        site = self.context
        
        # Need to use ancient Z2 property sheet API here...
        portal_memberdata = getToolByName(site, "portal_memberdata")
    
        # When new member is created, it's MemberData
        # is populated with the values from portal_memberdata property sheet,
        # so value="" will be the default value for users' home_folder_uid
        # member property
        
        fields = ['telefone',
                  # 'orgaoresposavel',
                  'uf',
                  'municipio',]
        
        for field in fields: 
            if not portal_memberdata.hasProperty(field):
                portal_memberdata.manage_addProperty(id=field, value="", type="string")
        
        #Criado o campo de ativação do usuário
        if not portal_memberdata.hasProperty('activate'):
            portal_memberdata.manage_addProperty(id='activate', value=False, type="boolean")
        
        #Criado o campo de uuid do usuário
        if not portal_memberdata.hasProperty('uuid'):
                portal_memberdata.manage_addProperty(id='uuid', value="", type="string")
        
                
    # Actions validators
    def validate_registration(self, action, data, errors):
        # CSRF protection
        CheckAuthenticator(self.request)

        registration = getToolByName(self.context, 'portal_registration')

        # ConversionErrors have no field_name attribute... :-(
        error_keys = [
            error.field.getName()
            for error
            in action.form.widgets.errors
        ]

        form_field_names = [f for f in self.fields]

        portal = getUtility(ISiteRoot)

        # passwords should match
        if 'password' in form_field_names:
            assert('password_ctl' in form_field_names)
            # Skip this check if password fields already have an error
            if not ('password' in error_keys or \
                    'password_ctl' in error_keys):
                password = self.widgets['password'].value
                password_ctl = self.widgets['password_ctl'].value
                if password != password_ctl:
                    err_str = 'Passwords do not match.'
                    notifyWidgetActionExecutionError(action,
                                                     'password', err_str)
                    notifyWidgetActionExecutionError(action,
                                                     'password_ctl', err_str)
        # Password field checked against RegistrationTool
        if 'password' in form_field_names:
            # Skip this check if password fields already have an error
            if not 'password' in error_keys:
                password = self.widgets['password'].value
                if password:
                    # Use PAS to test validity
                    err_str = registration.testPasswordValidity(password)
                    if err_str:
                        notifyWidgetActionExecutionError(action,
                                                         'password', err_str)

        username = ''
        email = ''
        try:
            email = self.widgets['email'].value
        except InputErrors, exc:
            # WrongType?
            errors.append(exc)
            
        username_field = 'email'

        # Generate a nice user id and store that in the data.
        username = self.generate_user_id(data)

        # check if username is valid
        # Skip this check if username was already in error list
        if not username_field in error_keys:
            if username == portal.getId():
                err_str = "This username is reserved. Please choose a different name."
                notifyWidgetActionExecutionError(action,
                                                 username_field, err_str)

        # check if username is allowed
        if not username_field in error_keys:
            if not registration.isMemberIdAllowed(username):
                err_str = "The login name you selected is already in use or is not valid. Please choose another."
                notifyWidgetActionExecutionError(action,
                                                 username_field, err_str)

        # Skip this check if email was already in error list
        if not 'email' in error_keys:
            if 'email' in form_field_names:
                if not registration.isValidEmail(email):
                    err_str = 'You must enter a valid email address.'
                    notifyWidgetActionExecutionError(action,
                                                 'email', err_str)

        if not 'email' in error_keys:
            pas = getToolByName(self, 'acl_users')
            # TODO: maybe search for lowercase as well.
            results = pas.searchUsers(login=email, exact_match=True)
            if results:
                err_str = "The login name you selected is already in use or is not valid. Please choose another."
                notifyWidgetActionExecutionError(action,
                                                 'email', err_str)

        if 'password' in form_field_names and not 'password' in error_keys:
            # Admin can either set a password or mail the user (or both).
            if not (self.widgets['password'].value or
                    self.widgets['mail_me'].value):
                err_str = _('msg_no_password_no_mail_me',
                            default=u"You must set a password or choose to "
                            "send an email.")
                notifyWidgetActionExecutionError(action, 'password', err_str)
                notifyWidgetActionExecutionError(action, 'mail_me', err_str)
        return errors
                
    def generate_user_id(self, data):
        """Generate a user id from data.

        The data is the data passed in the form.  Note that when email
        is used as login, the data will not have a username.

        There are plans to add some more options and add a hook here
        so it is possible to use a different scheme here, for example
        creating a uuid or creating bob-jones-1 based on the fullname.

        This will update the 'username' key of the data that is passed.
        """
        default = data.get('username') or data.get('email') or ''
        data['username'] = default
        return default
    
    
class ActivateAccount(grok.View):
    """
        View que ativa o usuário
        
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('activate-account')
    
    def update(self):
        form = self.request.form
        username  = form.get('u', None)
        token  = form.get('t', None)
        redirect_to = self.context.portal_url()
        
        
        if username and token:
            p_membership = getToolByName(self.context, 'portal_membership')
            member = p_membership.getMemberById(username)
            if member \
               and (member.getProperty('uuid') == token) \
               and hasattr(member, 'activate'):
                messages = IStatusMessage(self.request)
                messages.add(u"Obrigado por ativar sua conta, para continuar efetue o login abaixo.", type=u"info")
                member.setMemberProperties({'activate': True})
                redirect_to += '/login'
            
        self.request.response.redirect(redirect_to)
    
    def render(self):
        """No-op to keep grok.View happy
        """
        return ''
    
    
class ConfirmCreateUserView(grok.View):
    """
        View de confirmação para a criação do usuário
        
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('confirm-user-create')