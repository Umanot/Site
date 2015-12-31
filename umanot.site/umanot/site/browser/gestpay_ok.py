# -*- coding: utf-8 -*-
import logging
from Products.CMFCore.utils import getToolByName
from complexlab.orders.browser.process_order import ProcessOrder
from complexlab3.site.config import GP_ORDER_KEY

from zope.component import getUtility
from Products.Five import BrowserView
from complexlab3.site.browser.gestpay_soap import GestPaySoap
from complexlab3.site.browser.complexlab_utils import IComplexLabUtils


class GestpayOk(BrowserView):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.utils = getUtility(IComplexLabUtils)

    def __call__(self):
        response = self.request.RESPONSE

        form_data = self.request.form

        gpinfo = self.utils.getGestPayInfo(self.request)

        gps = GestPaySoap(gpinfo['host'], gpinfo['host_s2s'], '/gestpay/gestpayws/WSCryptDecrypt.asmx')
        results = gps.decrypt(form_data['a'], form_data['b'])

        logger = logging.getLogger('BancaSella:')
        logger.info(" -- OK")

        order_number = results.get('order_number')

        if not order_number:
            pass

        view = ProcessOrder(self.context, self.request)
        view.order_number = order_number
        view.action = 'confermato'
        view()

        #self.context.processOrder(self.context, order_id = order_number, action = 'confermato')

        brain = self.context.portal_catalog.unrestrictedSearchResults(
            portal_type = 'Order',
            getId = order_number,
        )

        if len(brain) == 1:
            order = self.context.unrestrictedTraverse(brain[0].getPath())
            order_info = order.getInfo()
            order.saveData({'xml': results['xml']}, GP_ORDER_KEY)

            mtool = getToolByName(self.context, 'portal_membership')
            auth = mtool.getAuthenticatedMember()

            message = '<p>Hai inserito un nuovo ordine su complexlab.it</p>'
            message += "<p><strong>Dettagli ordine</strong></h3>"
            message += "<p>Ordine numero: %s</p>" % self.utils.safeencode(order_number)
            message += "<p>Nome e cognome: %s</p>" % self.utils.safeencode(auth.getProperty('fullname') or auth.getProperty('username'))
            message += "<p>Indirizzo email: %s</p>" % self.utils.safeencode(auth.getProperty('email'))
            message += '<p><a href="http://www.complexlab.it/my-orders">Guarda i dettagli dei tuoi ordini</a></p>'
            message += '<hr />'
            message += '<p><strong>Dati di fatturazione</strong></p>'
            message += "<p>Cognome o ragione sociale: %s<br />" % self.utils.safeencode(order_info['invoice_lastname'])
            message += "Nome: %s<br />" % order_info['invoice_firstname']
            message += "Email: %s<br />" % order_info['invoice_email']
            message += "Telefono: %s<br />" % order_info['invoice_phone']
            message += "Indirizzo: %s<br />" % order_info['invoice_address']
            message += "CA: %s<br />" % order_info['invoice_zip_code']
            message += "Città: %s<br />" % order_info['invoice_city']
            message += "Provincia: %s<br />" % order_info['invoice_province']
            message += "Paese: %s<br />" % order_info['invoice_country']
            message += "Partita IVA o codice fiscale: %s</p>" % self.utils.safeencode(order_info['invoice_tax'])

            subject = "[ComplexLab] Ordine numero %s" % order_number

            clab_utils = getUtility(IComplexLabUtils)

            for email in ['francesco@mediatria.com', 'redazione@complexlab.it', 'angela.chirico@complexlab.it']:
                info = dict(
                    receiver = email,
                    subject = subject,
                    message = message,
                )

                clab_utils.notifySingleUser(info)


            #order.notifyCustomer()

        self.context.plone_utils.addPortalMessage(u'Ordine processato correttamente')
        return response.redirect('%s/i-nostri-servizi/pagina-di-ringraziamento-ecom/grazie-per-la-fiducia' % self.context.portal_url())