# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from Products.CMFPlone.utils import getToolByName, _createObjectByType

from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility

from umanot.orders.browser.products_view import IProductsView


class AddOrder(BrowserView):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.amount = request.get('amount')
        self.quantity = request.get('quantity')
        self.uid = request.get('uid')
        self.clab_utils = getUtility(IUmanotUtils)

    def __call__(self):
        response = self.request.RESPONSE

        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            # raise Unauthorized
            return response.redirect('%s/login_form' % self.context.absolute_url())

        if 'tos' not in self.request.form:
            IStatusMessage(self.request).add(u"Devi accettare le condizioni di vendita", type="error")
            self.request.response.redirect(self.context.absolute_url())
            return u""

        lang = self.request.get('LANGUAGE')

        order_folder = self.context.restrictedTraverse('/umanot/%s/orders' % lang)

        form_data = self.request.form

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

        net = self.clab_utils.float_from_money(self.amount) * int(self.quantity)

        catalog = getToolByName(self.context, 'portal_catalog')
        product = catalog(
            portal_type = "Product",
            UID = self.uid
        )
        if not len(product) == 1:
            return

        products_data = dict(
            title = product[0].Title,
            quantity = self.quantity
        )

        details = """<p>
          <span>Prodotto: %(title)s</span><br />
          <span>Quantità: %(quantity)s</span>
        </p>""" % products_data

        product_obj = product[0].getObject()

        nu_obj = _createObjectByType('Order', order_folder, id = obj_id, title = obj_title)
        nu_obj.setNumber(obj_id[len('ordine-'):])
        nu_obj.setUsername(auth.getMemberId())
        nu_obj.setEmail(auth.getProperty('email'))
        nu_obj.setDescription(products_data['title'])
        nu_obj.setText(details)
        nu_obj.setStatus('pending')
        nu_obj.setNet(net)
        nu_obj.setVat(product_obj.getVat())
        nu_obj.setProduct(product_obj)
        nu_obj.setQuantity(int(self.quantity))
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