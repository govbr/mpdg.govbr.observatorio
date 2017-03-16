# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from plone import api
from mpdg.govbr.observatorio.utilities.makelayoutobservatorio import MakeLayoutObservatorio


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'mpdg.govbr.observatorio:uninstall',
        ]

def create_folder_observatorio(portal):
    portal = api.portal.get()
    if 'sobre' not in portal:
        sobre = api.content.create(
            type='Folder',
            title='Sobre',
            id='sobre',
            container=portal)
    else:
        sobre = portal['sobre']

    if 'observatorio' not in sobre:
        observatorio = api.content.create(
            type='Folder',
            title='Observatório',
            id='observatorio',
            container=sobre)
    else:
        observatorio = sobre['observatorio']

    if 'capa' not in observatorio:
        capa = api.content.create(
            type='collective.cover.content',
            title='Observatório',
            id='capa',
            template_layout='Layout vazio',
            container=observatorio)
        MakeLayoutObservatorio(capa)
        # observatorio.manage_addProperty('default_page', capa.getId(), 'string')

def create_link_observatorio(portal):
    portal = api.portal.get()
    servicos = portal['servicos']
    if 'observatorio' not in servicos:
        link_biblioteca = api.content.create(
            type='Link',
            remoteUrl='${portal_url}/sobre/observatorio/',
            title='Observatório',
            container=servicos)

def create_folder_admin_observatorio(portal):
    portal = api.portal.get()
    if 'admin-observatorio' not in portal:
        admin = api.content.create(
            type='Folder',
            title='Administração Observatório',
            id='admin-observatorio',
            container=portal)

def link_pratica_pendentes(portal):
    portal = api.portal.get()
    folder = portal['admin-observatorio']
    if 'praticas-pendentes' not in folder:
        link_pratica_pendentes = api.content.create(
            type='Link',
            remoteUrl='${portal_url}/admin-observatorio/pratica-pendentes',
            title='Praticas Pendentes',
            container=folder)

def create_folder_contador(portal):
    portal = api.portal.get()
    if 'contador-de-acessos' not in portal:
        create_folder_contador = api.content.create(
            type='Folder',
            title='Contador de Acessos',
            container=portal)

def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.

def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
