from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IAddFollower(Interface):
    """
    Article view interface
    """


class AddFollower(BrowserView):
    """
    Article browser view
    """
    implements(IAddFollower)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = request.get('fw-errors', [])
        self.typology = 'comments' in request.get('type') == 'comments' else 'area_tematica'

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')
        
    @property
    def title(self):
        return self.context.Title()
        
    @property
    def description(self):
        return self.context.Description()