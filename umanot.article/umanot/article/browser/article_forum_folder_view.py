from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IArticleForumFolderView(Interface):
    """
    Article Forum Folder View view interface
    """


class ArticleForumFolderView(BrowserView):
    """
    Product browser view
    """
    implements(IArticleForumFolderView)

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
    def contents(self):
        brains = self.portal_catalog(
            portal_type = ["Article", "Placeholder"],
            path = '/'.join(self.context.getPhysicalPath()),
            sort_on = 'Date',
            sort_order = 'revese',
            getFeatured = False
        )

        results = []

        for brain in brains:
            obj = brain.getObject()
            info = obj.getInfo(scale="preview", width=276, height=-1)

            info['section'] = obj.aq_parent.Title()

            results.append(info)

        return results

    @property
    def featured(self):
        brains = self.portal_catalog(
            portal_type = ["Article", "Placeholder"],
            path = '/'.join(self.context.getPhysicalPath()),
            sort_on = 'Date',
            sort_order = 'revese',
            getFeatured = True
        )

        if not brains:
            return

        obj = brains[0].getObject()
        info = obj.getInfo(scale="preview", width=276, height=-1)

        info['section'] = obj.aq_parent.Title()

        return info