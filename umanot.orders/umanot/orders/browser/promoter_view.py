# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility
from zope.interface import implements, Interface

from Products.Five import BrowserView


class IPromoterView(Interface):
    """
    Order view interface
    """


class PromoterView(BrowserView):
    """
    Order browser view
    """
    implements(IPromoterView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.clab_utils = getUtility(IUmanotUtils)

    @property
    def title(self):
        return self.context.Title()

    @property
    def can_manage(self):
        mtool = getToolByName(self.context, 'portal_membership')

        if mtool.isAnonymousUser():
            return

        auth = mtool.getAuthenticatedMember()

        return auth.has_role('Manager')

    @property
    def info(self):
        return self.context.getInfo()

    @property
    def codes(self):
        codes = [x.getInfo() for x in self.context.getBRefs('discount_codes') if x]

        return codes

    def renderMoney(self, value):
        return self.clab_utils.money_from_float(value)
