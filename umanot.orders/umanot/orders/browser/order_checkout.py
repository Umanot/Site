# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from umanot.site.browser.umanot_utils import IUmanotUtils

from umanot.orders.config import COUNTRIES
from zope.component import getUtility
from zope.interface import implements, Interface

from Products.Five import BrowserView


class IOrderCheckout(Interface):
    """
    Order view interface
    """


class OrderCheckout(BrowserView):
    """
    Order browser view
    """
    implements(IOrderCheckout)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.order_number = request.get('order_number')
        self.discount_code = request.get('discount_code')
        self.utils = getUtility(IUmanotUtils)
        self.errors = request.get('co-errors', [])

    @property
    def title(self):
        return self.context.Title()

    def is_top(self):
        return "Top" in self.context.Title()

    def get_data(self):
        results = {}

        for k in ['lastname', 'firstname', 'address', 'zip_code', 'province', 'city', 'country', 'tax_code']:
            results[k] = self.request.get(k)

        if 'email' not in self.request.form:
            mtool = getToolByName(self.context, 'portal_membership')
            auth = mtool.getAuthenticatedMember()

            results['email'] = auth.getProperty('email')

        return results

    @property
    def order(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        brains = catalog.unrestrictedSearchResults(
            portal_type = "Order",
            getId = self.order_number
        )

        if not len(brains) == 1:
            return

        mtool = getToolByName(self.context, 'portal_membership')
        auth = mtool.getAuthenticatedMember()

        obj = self.context.unrestrictedTraverse(brains[0].getPath())

        if not (auth.has_role("Manager") or auth.getId() == obj.getUsername()):
            raise Unauthorized

        info = obj.getInfo()

        return info

    def renderMoney(self, value):
        return self.utils.money_from_float(value)

    @property
    def countries(self):
        data = COUNTRIES.items()
        data.sort(lambda x, y: cmp(x[1], y[1]))

        #data = [x for x in data if x[0] != 'IT']

        return data
