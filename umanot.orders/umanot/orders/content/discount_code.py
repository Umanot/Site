# -*- coding: utf-8 -*-
"""Definition of the Products content type
"""
from decimal import Decimal

from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from umanot.orders.interfaces.discount_code import IDiscountCode
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocument
from umanot.orders.config import PROJECTNAME

DiscountCodeSchema = document.ATDocumentSchema.copy() + atapi.Schema((
    atapi.StringField(
        name = 'code',
        required = True,
        storage = atapi.AnnotationStorage(),
        widget = atapi.DecimalWidget(
            label = u"Codice",
            size = 15
        )
    ),
    atapi.StringField(
        name = 'typology',
        required = True,
        storage = atapi.AnnotationStorage(),
        vocabulary = ['Sconto percentuale', 'Prezzo fisso', 'Sconto fisso'],
        widget = atapi.SelectionWidget(
            label = u"Tipo",
            format = 'select'
        )
    ),
    atapi.FloatField(
        name = 'amount',
        required = True,
        storage = atapi.AnnotationStorage(),
        widget = atapi.DecimalWidget(
            label = 'Importo o Percentuale',
        )
    ),
    atapi.StringField(
        name = 'net_or_gross',
        storage = atapi.AnnotationStorage(),
        vocabulary = ('Netto', 'Lordo'),
        widget = atapi.SelectionWidget(
            label = u"Prezzo netto / lordo",
            format = 'select'
        )
    ),
    atapi.ReferenceField(
        name = 'products',
        multiValued = True,
        relationship = 'discounted_products',
        widget = ReferenceBrowserWidget(
            label = u"Prodotti abbinati",
            startup_directory = '',
        ),
    ),
    atapi.ReferenceField(
        name = 'promoter',
        multiValued = False,
        relationship = 'discount_codes',
        widget = ReferenceBrowserWidget(
            label = u"Promoter abbinati",
            startup_directory = '',
        ),
    ),
    atapi.BooleanField(
        name = 'active',
        default = True,
        widget = atapi.BooleanWidget(
            label = u"Attivo",
        )
    )
))

DiscountCodeSchema['title'].storage = atapi.AnnotationStorage()
DiscountCodeSchema['title'].required = 1
DiscountCodeSchema['title'].searchable = 0
DiscountCodeSchema['description'].storage = atapi.AnnotationStorage()
DiscountCodeSchema['description'].required = 0
DiscountCodeSchema['description'].searchable = 0
DiscountCodeSchema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
DiscountCodeSchema['text'].required = 0
DiscountCodeSchema['text'].searchable = 0
DiscountCodeSchema['text'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

schemata.finalizeATCTSchema(DiscountCodeSchema)


class DiscountCode(ATDocument):
    """The DiscountCode item"""

    implements(IDiscountCode)

    portal_type = "DiscountCode"
    schema = DiscountCodeSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def getInfo(self):
        info = dict(
            uid = self.UID(),
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
            code = self.getCode(),
            typology = self.getTypology(),
            amount = self.getAmount(),
            promoter = self.getPromoter()
        )

        return info

    def get_prices_for_product(self, product):
        products = self.getProducts()

        net = product.getNet()
        tax = product.getVat()
        gross = self.get_gross_from_net(net, tax)

        typology = self.getTypology()
        amount = self.getAmount()

        if product in products:
            if typology == 'Sconto percentuale':
                net_discounted = net * (100 - amount) / 100.
                gross_discounted = self.get_gross_from_net(net_discounted, tax)
            elif typology == 'Prezzo fisso':
                if self.getNet_or_gross() == 'Netto':
                    net_discounted = amount
                    gross_discounted = self.get_gross_from_net(net_discounted, tax)
                else:
                    gross_discounted = amount
                    net_discounted = self.get_net_from_gross(gross_discounted, tax)
            elif typology == 'Sconto fisso':
                if self.getNet_or_gross() == 'Netto':
                    net_discounted = net - amount
                    gross_discounted = self.get_gross_from_net(net_discounted, tax)
                else:
                    gross_discounted = gross - amount
                    net_discounted = self.get_net_from_gross(gross_discounted, tax)
            else:  # non dovrebbe mai capitare
                net_discounted = ''
                gross_discounted = ''
        else:
            net_discounted = net
            gross_discounted = gross

        info = dict(
            net = net,
            tax = tax,
            gross = gross,
            net_discounted = net_discounted,
            gross_discounted = gross_discounted
        )

        return info

    def get_net_from_gross(self, gross, tax, decimal=False, safe_float=False):
        if safe_float:
            utils = getUtility(IUmanotUtils)
            gross = utils.float_from_money(gross)

        if decimal:
            return Decimal(gross * (1 - tax / 100.)).quantize(Decimal('.01'))
        else:
            return gross * (1 - tax / 100.)

    def get_gross_from_net(self, net, tax, decimal=False, safe_float=False):
        if safe_float:
            utils = getUtility(IUmanotUtils)
            net = utils.float_from_money(net)

        if decimal:
            return Decimal('%.15g' % (net / (1 - tax / 100.))).quantize(Decimal('.01'))
        else:
            return net / (1 - tax / 100.)


atapi.registerType(DiscountCode, PROJECTNAME)
