# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from umanot.site.browser.umanot_utils import IUmanotUtils

from umanot.site.browser.gestpay_soap import GestPaySoap
from zope.component import getUtility

from Products.Five import BrowserView



class GestpayCheckout(BrowserView):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.umanot_utils = getUtility(IUmanotUtils)

    def __call__(self):
        response = self.request.RESPONSE

        errors = {}

        for k, v in self.request.form.iteritems():
            self.request.form[k] = v.strip()

        mandatory = [] # ['lastname', 'address', 'zip_code', 'city', 'country', 'email', 'phone']

        for k in mandatory:
            if not self.request.form.get(k, '').strip():
                errors[k] = u"Questo campo è obbligatorio"

        if self.request.get('country') == 'IT' and not self.request.form.get('tax_code'):
            errors['tax_code'] = u"Questo campo è obbligatorio"

        if self.request.get('country') == 'IT' and not self.request.form.get('province'):
            errors['province'] = u"Questo campo è obbligatorio"

        if errors:
            self.request.form['co-errors'] = errors
            for k, v in self.request.form.items():
                self.request.form[k] = v

            IStatusMessage(self.request).addStatusMessage(u"Correggi gli errori evidenziati", type='error')
            return self.context.restrictedTraverse('@@order-checkout')()

        gpinfo = self.umanot_utils.getGestPayInfo(self.request)

        catalog = getToolByName(self.context, 'portal_catalog')

        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        omnipotent_user = OmnipotentUser()
        newSecurityManager(None, omnipotent_user)

        brains = catalog.unrestrictedSearchResults(
            portal_type = "Order",
            getId = self.request.form['order_number']
        )

        if brains:
            order = brains[0].getObject()
            order.setInvoice_lastname(self.request.get('lastname'))
            order.setInvoice_firstname(self.request.get('firstname'))
            order.setInvoice_phone(self.request.get('phone'))
            order.setInvoice_email(self.request.get('email'))
            order.setInvoice_address(self.request.get('address'))
            order.setInvoice_zip_code(self.request.get('zip_code'))
            order.setInvoice_city(self.request.get('city'))
            order.setInvoice_province(self.request.get('province'))
            order.setInvoice_country(self.request.get('country'))
            order.setInvoice_tax(self.request.get('tax_code'))

        newSecurityManager(None, user)

        # https://ecomms2s.sella.it/gestpay/gestpayws/wsCryptDecrypt.asmx
        gps = GestPaySoap(gpinfo['host'], gpinfo['host_s2s'], '/gestpay/gestpayws/WSCryptDecrypt.asmx')  # s2s

        amount = self.request.form['amount']

        if self.request.form.get('discount_code'):
            mtool = getToolByName(self.context, 'portal_membership')
            user = mtool.getAuthenticatedMember()
            omnipotent_user = OmnipotentUser()
            newSecurityManager(None, omnipotent_user)

            brains = catalog(portal_type = "DiscountCode")
            for brain in brains:
                obj = brain.getObject()
                if obj.getCode().lower() == self.request.form['discount_code'].lower():
                    order_brains = catalog(portal_type = "Order", getId=self.request.form['order_number'])
                    if order_brains:
                        order = order_brains[0].getObject()
                        product = order.getProduct()
                        quantity = order.getQuantity()

                        amount = '%0.2f' % float(obj.get_prices_for_product(product)['gross_discounted'] * quantity)

        if gpinfo['config'] == 'test':
            amount = '0.05'

        # import pdb; pdb.set_trace()
        # if self.context.portal_membership.getAuthenticatedMember().getId() == 'choco':
        #     amount = '0.05'

        redirect = gps.encrypt(gpinfo['user'], '242', amount, self.request.form['order_number'])

        return response.redirect(redirect)