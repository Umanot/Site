# -*- coding: utf-8 -*-
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.interface import implements, Interface

from Products.Five import BrowserView
from zope.component import getUtility


class IManageAdView(Interface):
    """
    Manage background view interface
    """


class ManageAdView(BrowserView):
    """
    Manage background browser view
    """
    implements(IManageAdView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.umanot_utils = getUtility(IUmanotUtils)

    @property
    def title(self):
        return self.context.Title()

    def images(self):
        images = self.umanot_utils.getAdImages()
        return images

    def actual(self):
        return self.umanot_utils.getLocalAd(self.context) or []
