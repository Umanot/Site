# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from plone import api


class IsAdminView(BrowserView):
    """
    IsAdminView browser view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        user = api.user

        if user.is_anonymous():
            return

        user_id = user.get_current().getId()

        return user_id in ['fdestino', 'max', 'red', 'nicolaantonucci', 'redazione-giovanni', 'redazione-elisa', 'angela.chirico', 'choco', 'zope']