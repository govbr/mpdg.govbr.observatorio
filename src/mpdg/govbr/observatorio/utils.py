# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from zope.component import getMultiAdapter


try:
    from email.utils import parseaddr, formataddr
except ImportError:
    # BBB for python2.4 (Plone 3)
    from email.Utils import parseaddr, formataddr

try:
    from zope.component.hooks import getSite
    # getSite
except ImportError:
    # BBB for Plone 3
    from zope.app.component.hooks import getSite

DEFAULT_CHARSET = 'utf-8'


def get_charset():
    """Character set to use for encoding the email.

    If encoding fails we will try some other encodings.  We hope
    to get utf-8 here always actually.

    The getSiteEncoding call also works when portal is None, falling
    back to utf-8.  But that is only on Plone 4, not Plone 3.  So we
    handle that ourselves.
    """
    charset = None
    portal = getSite()
    if portal is None:
        return DEFAULT_CHARSET
    charset = portal.getProperty('email_charset', '')
    if not charset:
        charset = getSiteEncoding(portal)
    return charset


def get_mail_host():
    """Get the MailHost object.

    Return None in case of problems.
    """
    portal = getSite()
    if portal is None:
        return None
    request = portal.REQUEST
    ctrlOverview = getMultiAdapter((portal, request),
        name='overview-controlpanel')
    mail_settings_correct = not ctrlOverview.mailhost_warning()
    if mail_settings_correct:
        mail_host = getToolByName(portal, 'MailHost', None)
        return mail_host


def get_mail_from_address():
    portal = getSite()
    if portal is None:
        return ''
    from_address = portal.getProperty('email_from_address', '')
    from_name = portal.getProperty('email_from_name', '')
    mfrom = formataddr((from_name, from_address))
    if parseaddr(mfrom)[1] != from_address:
        # formataddr probably got confused by special characters.
        mfrom = from_address
    return mfrom