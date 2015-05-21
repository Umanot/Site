from zope.interface import implements, Interface
from zope.component import getMultiAdapter

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName, _checkPermission
from DateTime import DateTime
from time import strftime

class IFollowThanksView(Interface):
    """
    FollowThanks view interface
    """


class FollowThanksView(BrowserView):
    """
    FollowThanks browser view
    """
    implements(IFollowThanksView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        self.mtool = getToolByName(self.context, 'portal_membership')

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
        
    @property
    def title(self):
        return self.context.Title()
        
    @property
    def description(self):
        return self.context.Description()
        