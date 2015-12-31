# -*- coding: utf-8 -*-
import logging
from umanot.site.config import GP_ORDER_KEY
from zope.component import getUtility

from Products.Five import BrowserView

from umanot.site.browser.gestpay_soap import GestPaySoap
from umanot.site.browser.umanot_utils import IUmanotUtils


class GestpayS2S(BrowserView):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.utils = getUtility(IUmanotUtils)

    def __call__(self):
        form_data = self.request.form

        self.context.plone_log(str(self.request))
        self.context.plone_log("==========================================================")
        self.context.plone_log(str(self.request.form))

        if not form_data.get('a'):
            return "<HTML></HTML>"

        gpinfo = self.utils.getGestPayInfo(self.request)

        gps = GestPaySoap(gpinfo['host'], gpinfo['host_s2s'], '/gestpay/gestpayws/WSCryptDecrypt.asmx')
        results = gps.decrypt(form_data['a'], form_data['b'])

        if 'clab_status' in results.keys():
            self.context.plone_log("################################# S2S ###########################")
            self.context.plone_log(str(results))
            return "<HTML></HTML>"

        logger = logging.getLogger('BancaSella:')
        logger.info(" -- S2S")

        order_number = results.get('order_number')

        if not order_number:
            pass

        if results['result'] == 'OK':
            self.utils.processOrder(self.context, order_number, 'confermato')

            brain = self.context.portal_catalog.unrestrictedSearchResults(
                portal_type = 'Order',
                getId = order_number,
            )

            if len(brain) == 1:
                order = self.context.unrestrictedTraverse(brain[0].getPath())
                order.saveData({'xml': results['xml']}, GP_ORDER_KEY)

                order.notifyCustomer()
        else:
            self.utils.processOrder(self.context, order_number, 'annullato')


        return "<HTML></HTML>"