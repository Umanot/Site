from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IPostView(Interface):
    """
    Article view interface
    """

class PostView(BrowserView):
    """
    Article browser view
    """
    implements(IPostView)

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
    def info(self):
        info = self.context.getInfo(scale="preview")

        return info