# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.tests.base.security import OmnipotentUser

from Products.Five import BrowserView


class ProcessOrder(BrowserView):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.order_number = request.get("order_number")
        self.action = request.get("action")

    def __call__(self):
        if not self.order_number or not self.action:
            return 'Error: missing data'

        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        omnipotent_user = OmnipotentUser()
        newSecurityManager(None, omnipotent_user)

        catalog = getToolByName(self.context, 'portal_catalog')

        lang = self.request.get('LANGUAGE')

        brain = catalog.unrestrictedSearchResults(
            portal_type = 'Order',
            path = '/umanot/%s/orders' % lang,
            getId = self.order_number,
        )

        if len(brain) != 1:
            newSecurityManager(None, user)
            return 'Error: no brain retrieved'

        order = self.context.unrestrictedTraverse(brain[0].getPath())

        order.processAction(self.action)

        newSecurityManager(None, user)

        return True