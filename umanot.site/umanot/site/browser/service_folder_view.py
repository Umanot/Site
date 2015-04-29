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
    def contents(self):
        brains = self.portal_catalog(
            portal_type = ["Document", "Article"],
            path = '/'.join(self.context.getPhysicalPath()),
            sort_on = 'getObjPositionInParent',
        )

        results = []

        for brain in brains:
            info = dict(
                title = brain.Title,
                description = brain.Description,
                URL = brain.getURL()
            )

            results.append(info)

        return results