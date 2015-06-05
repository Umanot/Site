# -*- coding: utf-8 -*-
import base64
from Products.CMFCore.utils import getToolByName
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility

from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
import datetime
import oursql


class INotifyFollowers(Interface):
    """
    NotifyFollowers view interface
    """


class NotifyFollowers(BrowserView):
    """
    NotifyFollowers browser view
    """
    implements(INotifyFollowers)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.umanot_utils = getUtility(IUmanotUtils)

    def __call__(self):
        request = self.request
        response = request.RESPONSE

        if self.context.portal_type in ['Article', 'Placeholder']:
            self.umanot_utils.notifyFollowers(self.context, 'area_tematica', 'new')
        elif self.context.portal_type == 'Discussion Item':
            self.umanot_utils.notifyFollowers(self.context, 'comments', 'new')