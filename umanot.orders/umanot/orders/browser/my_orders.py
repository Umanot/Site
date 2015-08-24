# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility
from zope.interface import implements, Interface

from Products.Five import BrowserView


class IMyOrdersView(Interface):
    """
    Order view interface
    """


class MyOrdersView(BrowserView):
    """
    Order browser view
    """
    implements(IMyOrdersView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.clab_utils = getUtility(IUmanotUtils)

    @property
    def title(self):
        return self.context.Title()

    @property
    def is_anonymous(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.isAnonymousUser()

    @property
    def orders(self):
        mtool = getToolByName(self.context, 'portal_membership')
        catalog = getToolByName(self.context, 'portal_catalog')

        if mtool.isAnonymousUser():
            return []

        auth = mtool.getAuthenticatedMember()

        brains = catalog(
            portal_type = "Order",
            sort_on = 'created'
        )

        results = []

        for brain in brains:
            obj = self.context.unrestrictedTraverse(brain.getPath())

            if not auth.has_role('Manager') and obj.getUsername() != auth.getId():
                continue

            info = obj.getInfo()

            results.append(info)

        return results

    def renderMoney(self, value):
        return self.clab_utils.money_from_float(value)