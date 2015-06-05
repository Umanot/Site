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


class INotifyUpdate(Interface):
    """
    NotifyUpdate view interface
    """


class NotifyUpdate(BrowserView):
    """
    NotifyUpdate browser view
    """
    implements(INotifyUpdate)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.umanot_utils = getUtility(IUmanotUtils)

    def __call__(self):
        request = self.request
        response = request.RESPONSE

        import pdb; pdb.set_trace()

        if self.context.portal_type in ['Article', 'Placeholder']:
            self.umanot_utils.notifyFollowers(self.context, 'area_tematica', 'update')