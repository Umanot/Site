from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IArticleView(Interface):
    """
    Article view interface
    """

class ArticleView(BrowserView):
    """
    Article browser view
    """
    implements(IArticleView)

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
        section = self.context.aq_parent
        info['section'] = section.Title()
        info['section_url'] = section.absolute_url()

        return info