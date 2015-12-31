# -*- coding: utf-8 -*-
import logging
from complexlab3.site.browser.complexlab_utils import IComplexLabUtils
from zope.component import getUtility

from Products.Five import BrowserView

from complexlab3.site.browser.gestpay_soap import GestPaySoap


class GestpayFail(BrowserView):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.utils = getUtility(IComplexLabUtils)

    def __call__(self):
        response = self.request.RESPONSE

        form_data = self.request.form

        gpinfo = self.utils.getGestPayInfo(self.request)

        logger = logging.getLogger('BancaSella:')
        logger.info(" -- FAIL")

        gps = GestPaySoap(gpinfo['host'], gpinfo['host_s2s'], '/gestpay/gestpayws/WSCryptDecrypt.asmx')
        results = gps.decrypt(form_data['a'], form_data['b'])

        order_number = results.get('order_number')

        if not order_number:
            pass

        self.utils.processOrder(self.context, order_number, 'annullato')

        self.context.plone_utils.addPortalMessage(u'Ordine annullato')
        return response.redirect('%s' % self.context.portal_url())