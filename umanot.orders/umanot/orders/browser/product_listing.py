# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, Interface

from Products.Five import BrowserView


class IProductListing(Interface):
    """
    Order view interface
    """


class ProductListing(BrowserView):
    """
    Order browser view
    """
    implements(IProductListing)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()

    def text_to_html(self, text):
        transform = getattr(getToolByName(self.context, 'portal_transforms'), 'text_to_html')
        return transform.convertTo('text/x-html-safe', text)._data

    @property
    def is_anonymous(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.isAnonymousUser()

    @property
    def contents(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(
            portal_type = "Product",
            path = '/'.join(self.context.getPhysicalPath()),
            sort_on = 'getObjPositionInParent',
        )

        results = []

        for brain in brains:
            results.append(brain.getObject().getInfo())

        return results