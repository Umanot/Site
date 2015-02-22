from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface


class IHomepageView(Interface):
    """
    Homepage view interface
    """


class HomepageView(BrowserView):
    """
    Homepage browser view
    """
    implements(IHomepageView)

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
    def is_manager(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return not mtool.isAnonymousUser() and mtool.getAuthenticatedMember().has_role('Manager')

    @property
    def info(self):
        return self.context.getInfo()

    @property
    def articles(self):
        brains = self.portal_catalog(
            portal_type = "Article",
            sort_on = 'Date',
            sort_order = 'reverse',
            sort_limit = 20
        )

        news = []

        pt = getToolByName(self.context, 'portal_transforms')

        for brain in brains:
            description = brain.Description

            if not description:
                text = brain.getObject().getText()
                description = pt.html_to_text.convertTo('text/plain', text)._data.strip()

            if len(description.split(' ')) > 50:
                description = ' '.join(description.split(' ')[:50])
                description += '...'
            info = dict(
                title = brain.Title,
                description = description,
                URL = brain.getURL(),
            )

            news.append(info)

        return news
