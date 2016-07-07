# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from complexlab3.site.browser.complexlab_utils import IComplexLabUtils

from plone import api
from zope.interface import implements, Interface

from Products.Five import BrowserView
from zope.component._api import getMultiAdapter, getUtility
from zope.i18nmessageid import MessageFactory


class IsAdminView(BrowserView):
    """
    IsAdminView browser view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.clab_utils = getUtility(IComplexLabUtils)

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')

        user = api.user

        if user.is_anonymous():
            return

        user_id = user.get_current().getId()

        return user_id in ['fdestino', 'max', 'red', 'nicolaantonucci', 'redazione-giovanni', 'redazione-elisa', 'angela.chirico', 'choco', 'zope']