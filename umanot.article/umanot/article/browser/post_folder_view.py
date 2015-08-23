from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface


class IPostFolderView(Interface):
    """
    Article Forum Folder View view interface
    """


class PostFolderView(BrowserView):
    """
    Product browser view
    """
    implements(IPostFolderView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.limit = 2
        self.last_uid = request.get('last_uid')

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
            portal_type = ["Post"],
            path = '/'.join(self.context.getPhysicalPath()),
            sort_on = 'Date',
            sort_order = 'revese',
        )

        uids = [brain.UID for brain in brains]

        if self.last_uid:
            try:
                show_more_index = uids.index(self.last_uid) + 1
            except ValueError:
                show_more_index = 0
        else:
            show_more_index = 0

        if show_more_index:
            brains = brains[show_more_index:]

        results = {'data': [], 'last_uid': None}

        for brain in brains:
            obj = brain.getObject()
            info = obj.getInfo(scale = "preview", width = 276, height = -1)

            info['section'] = obj.aq_parent.Title()

            results['data'].append(info)

            if len(results['data']) == self.limit:
                break

        if results['data']:
            results['last_uid'] = results['data'][-1]['uid']

        return results
