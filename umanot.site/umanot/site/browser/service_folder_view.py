from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IServiceFolderView(Interface):
    """
    Service view interface
    """


class ServiceFolderView(BrowserView):
    """
    Service browser view
    """
    implements(IServiceFolderView)

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
        