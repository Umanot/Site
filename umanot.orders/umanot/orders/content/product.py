# -*- coding: utf-8 -*-
"""Definition of the Products content type
"""
import math
from decimal import Decimal

from umanot.orders.browser.interfaces import IEcomSettings
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocument
from umanot.orders.config import PROJECTNAME
from umanot.orders.interfaces.product import IProduct

ProductSchema = document.ATDocumentSchema.copy() + atapi.Schema((
    atapi.FloatField(
        name = 'net',
        required = True,
        storage = atapi.AnnotationStorage(),
        widget = atapi.DecimalWidget(
            label = u"Prezzo (netto)"
        )
    ),
    atapi.IntegerField(
        name = 'vat',
        storage = atapi.AnnotationStorage(),
        default = 22,
        widget = atapi.IntegerWidget(
            label = u"IVA",
        )
    ),
    atapi.IntegerField(
        name = 'min',
        storage = atapi.AnnotationStorage(),
        default = 1,
        widget = atapi.IntegerWidget(
            label = u"Quantità minima",
        )
    ),
    atapi.IntegerField(
        name = 'max',
        storage = atapi.AnnotationStorage(),
        default = 0,
        widget = atapi.IntegerWidget(
            label = u"Quantità massima",
        )
    ),
    atapi.BooleanField(
        name = 'consulenza',
        widget = atapi.BooleanWidget(
            label = u"Consulenza",
        ),
    ),
))

ProductSchema['title'].storage = atapi.AnnotationStorage()
ProductSchema['title'].required = 1
ProductSchema['title'].searchable = 0
ProductSchema['description'].storage = atapi.AnnotationStorage()
ProductSchema['description'].required = 0
ProductSchema['description'].searchable = 0
# ProductSchema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
ProductSchema['text'].required = 0
ProductSchema['text'].searchable = 0
# ProductSchema['text'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

schemata.finalizeATCTSchema(ProductSchema)


class Product(ATDocument):
    """The Product item"""

    implements(IProduct)

    portal_type = "Product"
    schema = ProductSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def getInfo(self):
        min = self.getMin()
        max = self.getMax()

        net = self.getNet()
        vat = self.getVat()

        info = dict(
            uid = self.UID(),
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
            text = self.getText(),
            net = net,
            gross = self.get_gross_from_net(net, vat),
            min = min,
            max = max,
            has_range = min and max > min,
            consulenza = self.getConsulenza(),
            dollars = self.getDollars()
        )

        return info

    def getDollars(self):
        settings = getUtility(IEcomSettings, 'umanot.ecom_settings')

        net = self.getNet()
        vat = self.getVat()

        threshold = settings.threshold
        cambio = settings.cambio

        if settings.round_net:
            info = {
                'net': int(math.floor(net * cambio / float(threshold))) * threshold
            }

            info['gross'] = self.get_gross_from_net(info['net'], vat)
        else:
            gross = self.get_gross_from_net(net, vat)
            info = {
                'gross': int(math.floor(gross * cambio / float(threshold))) * threshold
            }

            info['net'] = self.get_net_from_gross(info['gross'], vat)

        return info


    def get_gross_from_net(self, net, tax, decimal=False, safe_float=False):
        if safe_float:
            utils = getUtility(IUmanotUtils)
            net = utils.float_from_money(net)

        if decimal:
            return Decimal(net * (1 + tax / 100.)).quantize(Decimal('.01'))
        else:
            return net * (1 + tax / 100.)

    def get_net_from_gross(self, gross, tax, decimal=False, safe_float=False):
        if safe_float:
            utils = getUtility(IUmanotUtils)
            gross = utils.float_from_money(gross)

        tax_adj = 1 + tax / 100.
        if decimal:
            return Decimal('%.15g' % (gross / tax_adj)).quantize(Decimal('.01'))
        else:
            return gross / tax_adj

        # if decimal:
        #     return Decimal(gross * (1 - tax / 100.)).quantize(Decimal('.01'))
        # else:
        #     return gross * (1 - tax / 100.)



atapi.registerType(Product, PROJECTNAME)