# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from umanot.site.browser.umanot_utils import IUmanotUtils
from plone.memoize.instance import memoize
from zope.component import getUtility
from zope.interface import implements, Interface

from Products.Five import BrowserView


class IProductView(Interface):
    """
    Order view interface
    """


class ProductView(BrowserView):
    """
    Order browser view
    """
    implements(IProductView)

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
    def is_anonymous(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.isAnonymousUser()

    @property
    @memoize
    def info(self):
        return self.context.getInfo()

    @property
    def discount_info(self):
        if not self.request.get('code'):
            return

        code = self.request['code']

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type = "DiscountCode",
        )

        objs = [self.context.unrestrictedTraverse(x.getPath()) for x in brains]

        codes = [x for x in objs if x.getCode().lower().strip() == code.lower().strip()]

        for code in codes:
            if self.context not in code.getProducts():
                continue

            return code.get_prices_for_product(self.context)

    def renderMoney(self, value):
        return self.clab_utils.money_from_float(value)