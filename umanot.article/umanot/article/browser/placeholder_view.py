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
        return self.context.getInfo(scale="preview")