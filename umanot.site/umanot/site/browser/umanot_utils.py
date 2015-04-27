# -*- coding: utf-8 -*-
import copy

from zope.interface import implements, Interface
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite


class IUmanotUtils(Interface):
    """sol utility"""


class UmanotUtils(object):
    implements(IUmanotUtils)

    def is_stage(self, request):
        if 'localhost' in request.get('URL') or 'mediatria.com' in request.get('URL'):
            return True

    # def getSector(self, context):
    #     parent = context.aq_inner
    #     try:
    #         while parent.portal_type != 'Sector':
    #             parent = parent.aq_parent
    #         return parent
    #     except:
    #         return None

    def sendmail(self, mailfrom, mailto, mailBody, subject=None, debug=False):
        """"""
        site = getSite()
        subtype = 'text/html'
        mail_host = getattr(site, 'MailHost', None)

        subject = self.safeencode(subject)
        mailBody = self.safeencode(mailBody)

        if debug:
            site.plone_log('Sending mail to: %s - %s - %s' % (mailto, subject, mailBody))

        # mail_host.send(mailBody, mto=mailto, mfrom=mailfrom, subject=subject, msg_type=subtype)
        mail_host.send(mailBody, mto = mailto, mfrom = mailfrom, subject = subject, msg_type = subtype, charset = 'utf-8')

    def safeencode(self, v):
        if isinstance(v, unicode):
            return v.encode('utf-8')
        return v

    def safedecode(self, v):
        if isinstance(v, str):
            return v.decode('utf-8')
        return v