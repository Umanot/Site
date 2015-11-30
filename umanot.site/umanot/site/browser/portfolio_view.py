from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility
from zope.interface import implements, Interface

class IPortfolioView(Interface):
    """
    Article Folder View view interface
    """


class PortfolioView(BrowserView):
    """
    Product browser view
    """
    implements(IPortfolioView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portfolio = request.get('portfolio')
        self.umanot_utils = getUtility(IUmanotUtils)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')
        
    @property
    def title(self):
        return self.context.Title()
        
    @property
    def description(self):
        return self.context.Description()

    def get_data(self):
        self.umanot_utils.get_posts_by_portfolio(self.portfolio)