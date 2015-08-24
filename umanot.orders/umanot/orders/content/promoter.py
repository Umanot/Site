# -*- coding: utf-8 -*-
"""Definition of the Products content type
"""
from umanot.orders.interfaces.promoter import IPromoter

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocument
from umanot.orders.config import PROJECTNAME

PromoterSchema = document.ATDocumentSchema.copy() + atapi.Schema((
))

PromoterSchema['title'].storage = atapi.AnnotationStorage()
PromoterSchema['title'].required = 1
PromoterSchema['title'].searchable = 0
PromoterSchema['description'].storage = atapi.AnnotationStorage()
PromoterSchema['description'].required = 0
PromoterSchema['description'].searchable = 0
PromoterSchema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
PromoterSchema['text'].required = 0
PromoterSchema['text'].searchable = 0
PromoterSchema['text'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

schemata.finalizeATCTSchema(PromoterSchema)


class Promoter(ATDocument):
    """The Promoter item"""

    implements(IPromoter)

    portal_type = "Promoter"
    schema = PromoterSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def getInfo(self):
        info = dict(
            uid = self.UID(),
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
        )

        return info


atapi.registerType(Promoter, PROJECTNAME)
