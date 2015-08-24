# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility
from zope.interface import implements, Interface

from Products.Five import BrowserView


class IDiscountCodeView(Interface):
    """
    Order view interface
    """


class DiscountCodeView(BrowserView):
    """
    Order browser view
    """
    implements(IDiscountCodeView)

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
    def products(self):
        # catalog = getToolByName(self.context, 'portal_catalog')
        # brains = catalog(
        #     portal_type = "Product",
        #     sort_on = 'sortable_title'
        # )
        #
        # results = []
        #
        # for brain in brains:
        #     info = dict(
        #         uid = brain.UID,
        #         title = brain.Title,
        #         description = brain.Description,
        #         URL = brain.getURL(),
        #         prices = self.context.get_prices_for_product(brain.getObject())
        #     )
        #
        #     results.append(info)
        results = []
        objs = [x for x in self.context.getProducts() if x and x.portal_type == "Product"]

        for obj in objs:
            info = dict(
                uid = obj.UID(),
                title = obj.Title(),
                description = obj.Description(),
                URL = obj.absolute_url(),
                prices = self.context.get_prices_for_product(obj)
            )
            results.append(info)

        return results

    def renderMoney(self, value):
        return self.clab_utils.money_from_float(value)
