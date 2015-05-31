# -*- coding: utf-8 -*-
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component._api import getUtility


class IProcessManageAdView(Interface):
    """
    ProcessManageAdView view interface
    """


class ProcessManageAdView(BrowserView):
    """
    ProcessManageAdView browser view
    """
    implements(IProcessManageAdView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.umanot_utils = getUtility(IUmanotUtils)

    def __call__(self):
        response = self.request.RESPONSE

        data = {'top': [], 'bottom': []}
        for k, v in self.request.form.iteritems():
            if k.startswith('image-top-') and v == 'on':
                data['top'].append(k[len('image-top-'):])
            elif k.startswith('image-bottom-') and v == 'on':
                data['bottom'].append(k[len('image-bottom-'):])

        self.umanot_utils.setLocalAd(self.context, data)

        IStatusMessage(self.request).addStatusMessage(u"Dati aggiornati correttamente", type = 'info')
        return response.redirect(self.context.absolute_url())
