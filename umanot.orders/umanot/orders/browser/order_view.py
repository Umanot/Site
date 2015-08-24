# -*- coding: utf-8 -*-
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility
from zope.interface import implements, Interface

from Products.Five import BrowserView


class IOrderView(Interface):
    """
    Order view interface
    """


class OrderView(BrowserView):
    """
    Order browser view
    """
    implements(IOrderView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.clab_utils = getUtility(IUmanotUtils)

    @property
    def title(self):
        return self.context.Title()

    @property
    def discount_code(self):
        return self.context.getDiscount_code()

    @property
    def customer(self):
        return self.context.getCustomer()

    @property
    def info(self):
        return self.context.getInfo()

    def renderMoney(self, value):
        return self.clab_utils.money_from_float(value)