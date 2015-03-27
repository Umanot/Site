from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IUmanotDocumentView(Interface):
    """
    Umanot Document view interface
    """


class UmanotDocumentView(BrowserView):
    """
    Umanot Document browser view
    """
    implements(IUmanotDocumentView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')
        
    @property
    def title(self):
        return self.context.Title()
        
    @property
    def description(self):
        return self.context.Description()
        
    @property
    def info(self):
        return self.context.getInfo()
        