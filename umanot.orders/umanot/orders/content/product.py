# -*- coding: utf-8 -*-
"""Definition of the Products content type
"""

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

        info = dict(
            uid = self.UID(),
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
            text = self.getText(),
            net = self.getNet(),
            min = min,
            max = max,
            has_range = min and max > min,
            consulenza = self.getConsulenza()
        )

        return info


atapi.registerType(Product, PROJECTNAME)