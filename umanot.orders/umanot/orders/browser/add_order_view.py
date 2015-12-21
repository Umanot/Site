# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from Products.CMFPlone.utils import getToolByName, _createObjectByType

from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility

from umanot.orders.browser.products_view import IProductsView


class AddOrderView(BrowserView):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.quantity = int(request['quantity']) if request.get('quantity') else 1
        self.code = request.get('code')
        self.uid = request.get('uid')
        self.clab_utils = getUtility(IUmanotUtils)

    def __call__(self):
        response = self.request.RESPONSE

        if 'form.discount.check' in self.request.form:
            redirect = '%s?code=%s' % (self.context.absolute_url(), self.request.form.get('code'))
            response.redirect(redirect)
            return u""

        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            # raise Unauthorized
            return response.redirect('%s/login_form' % self.context.absolute_url())

        if 'tos' not in self.request.form:
            IStatusMessage(self.request).add(u"Devi accettare le condizioni di vendita", type="error")
            response.redirect(self.context.absolute_url())
            return u""

        lang = self.request.get('LANGUAGE')

        order_folder = self.context.restrictedTraverse('/umanot/%s/orders' % lang)

        today = DateTime()
        year = '%d' % today.year()
        year = year[2:]

        date_prefix = '%02d%s' % (today.month(), year)

        obj_id = 'ordine-%s01' % date_prefix
        if obj_id in [r[0] for r in order_folder.items()]:
            while obj_id in [r[0] for r in order_folder.items()]:
                counter = int(obj_id[-2:])
                obj_id = 'ordine-%s%02d' % (date_prefix, counter + 1)

        obj_title = obj_id.capitalize().replace('-', ' ')

        auth = mtool.getAuthenticatedMember()

        catalog = getToolByName(self.context, 'portal_catalog')
        products = catalog(
            portal_type = "Product",
            UID = self.uid
        )

        if not len(products) == 1:
            return

        product = products[0].getObject()

        unit_net = product.getNet()
        total_net = self.quantity * unit_net

        discount_info = None
        if self.code:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog.unrestrictedSearchResults(
                portal_type = "DiscountCode",
            )

            objs = [self.context.unrestrictedTraverse(x.getPath()) for x in brains]

            codes = [x for x in objs if x.getCode().lower().strip() == self.code.lower().strip()]

            for code in codes:
                if self.context not in code.getProducts():
                    continue

                discount_info = code.get_prices_for_product(self.context)

        products_data = dict(
            title = self.clab_utils.safeencode(product.Title()),
            quantity = self.quantity,
            unit_net = unit_net,
            total_net = total_net,
            discount_code = self.clab_utils.safeencode(self.code),
            vat = product.getVat(),
            discount_info = discount_info
        )

        details = """<p>
          <span>Prodotto: %(title)s</span><br />
          <span>Quantità: %(quantity)s</span><br />
          <span>Prezzo unitario non scontato: %(unit_net)s</span><br />
          <span>IVA: %(vat)s</span><br />
          <span>Totale netto: %(total_net)s</span><br />""" % products_data

        details = self.clab_utils.safeencode(details)

        if discount_info:
            details += "<span>Codice sconto: %(discount_code)s</span><br />" % products_data
            details += "<span>Netto scontato: %(net_discounted)s</span><br />" % products_data['discount_info']
            details += "<span>Lordo scontato: %(gross_discounted)s</span><br/>" % products_data['discount_info']
        else:
            details += "<span>Codice sconto: --</span><br/>"

        details += "</p>"

        if discount_info:
            total_net = discount_info['net_discounted']

        nu_obj = _createObjectByType('Order', order_folder, id = obj_id, title = obj_title)
        nu_obj.setNumber(obj_id[len('ordine-'):])
        nu_obj.setUsername(auth.getMemberId())
        nu_obj.setEmail(auth.getProperty('email'))
        nu_obj.setDescription(products_data['title'])
        nu_obj.setText(details)
        nu_obj.setStatus('pending')
        nu_obj.setNet(total_net)
        nu_obj.setVat(product.getVat())
        nu_obj.setProduct(product)
        nu_obj.setQuantity(self.quantity)
        nu_obj.reindexObject()

        products_folder = catalog(
            portal_type = "Folder",
            object_provides = IProductsView.__identifier__,
        )

        if products_folder:
            products_folder_obj = products_folder[0].getObject()
            if hasattr(products_folder_obj, 'ordina'):
                redirect_obj = getattr(products_folder_obj, 'ordina')
                redirect_url = redirect_obj.absolute_url()
            else:
                redirect_url = self.context.absolute_url()

        else:
            redirect_url = self.context.absolute_url()

        return response.redirect('%s/@@order-checkout?order_number=%s' % (redirect_url, obj_id))