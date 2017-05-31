import itertools
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from umanot.site.browser.interfaces import IHomepageServices, IHomepageFeatures, IHomepageMosaic, IHomepageSlides

from plone import api
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
    def news(self):
        if not self.context.getShow_news():
            return []

        brains = self.portal_catalog(
            portal_type = "News Item",
            sort_on = 'Date',
            sort_order = 'reverse',
            review_state = 'published'
        )

        results = []

        for brain in brains:
            obj = brain.getObject()

            has_image = obj.getImage() and obj.getImage().get_size()

            image = obj.tag(scale="mini") if has_image else ''

            info = dict(
                title = brain.Title,
                description = brain.Description,
                URL = brain.getURL(),
                image = image
            )

            results.append(info)

        return results

    @property
    def slides(self):
        folders = self.portal_catalog(
            portal_type = "Folder",
            object_provides = IHomepageSlides.__identifier__
        )

        if not folders:
            return

        folder = folders[0]

        brains = self.portal_catalog(
            portal_type = "Slide",
            path = folder.getPath(),
            sort_on = 'getObjPositionInParent',
        )

        results = []

        for brain in brains:
            obj = brain.getObject()
            info = obj.getInfo()
            info['slide_url'] = brain.getURL()
            results.append(info)

        return results

    @property
    def articles(self):
        brains = self.portal_catalog(
            portal_type = ["Article", "Placeholder"],
            sort_on = 'Date',
            sort_order = 'reverse',
            sort_limit = 20,
            getHomepage_featured = True
        )

        results = []

        for brain in brains:
            obj = brain.getObject()
            info = obj.getInfo(scale="preview", width=276, height=-1)

            info['section'] = obj.aq_parent.Title()

            results.append(info)

        results.sort(lambda x,y: cmp(y['sortable_date'], x['sortable_date']))

        return results

    @property
    def services(self):
        folders = self.portal_catalog(
            portal_type = "Folder",
            object_provides = IHomepageServices.__identifier__
        )

        if not folders:
            return

        folder = folders[0]

        brains = self.portal_catalog(
            portal_type = "Document",
            path = folder.getPath(),
            sort_on = 'getObjPositionInParent',
        )

        results = []

        for brain in brains:
            obj = brain.getObject()
            info = dict(
                title = brain.Title,
                description = brain.Description.strip(),
                text = obj.getText()
            )

            related = [x for x in obj.getRelatedItems() if x]
            info['URL'] = related[0].absolute_url() if related else None

            results.append(info)

        return results

    @property
    def mosaic(self):
        folders = self.portal_catalog(
            portal_type = "Folder",
            object_provides = IHomepageMosaic.__identifier__
        )

        if not folders:
            return

        folder = folders[0]

        brains = self.portal_catalog(
            portal_type = "Document",
            path = folder.getPath(),
            sort_on = 'getObjPositionInParent',
        )

        results = []

        for brain in brains:
            obj = brain.getObject()
            info = dict(
                title = brain.Title,
                description = brain.Description.strip(),
                text = obj.getText()
            )

            related = [x for x in obj.getRelatedItems() if x]
            info['URL'] = related[0].absolute_url() if related else None

            results.append(info)

        return results

    @property
    def services(self):
        folders = self.portal_catalog(
            portal_type = "Folder",
            object_provides = IHomepageServices.__identifier__
        )

        if not folders:
            return

        folder = folders[0]

        brains = self.portal_catalog(
            portal_type = "Document",
            path = folder.getPath(),
            sort_on = 'getObjPositionInParent',
        )

        results = []

        for brain in brains:
            obj = brain.getObject()

            info = dict(
                id = brain.getId,
                title = brain.Title,
                icon = brain.Description.strip().replace('fa-', ''),
                text = obj.getText(),
            )

            related = [x for x in obj.getRelatedItems() if x]

            if brain.getId == 'osserva-umanot-in-azione':
                url = '/it/servizi/osserva-umanot'
            elif brain.getId == 'monitor-umanot-in-action':
                url = '/en/services/observe-umanot-in-action-1'
            elif related:
                related_obj = related[0]
                parent = related_obj.aq_parent
                url = '%s#%s' % (parent.absolute_url(), related_obj.getId())
            else:
                url = '#'

            info['URL'] = url

            results.append(info)

        return results

    def is_choco(self):
        return api.user.get_current().getUserName() == 'choco'

    @property
    def features(self):
        folders = self.portal_catalog(
            portal_type = "Folder",
            object_provides = IHomepageFeatures.__identifier__
        )

        if not folders:
            return

        folder = folders[0]

        brains = self.portal_catalog(
            portal_type = "Document",
            path = folder.getPath(),
            sort_on = 'getObjPositionInParent',
        )

        results = []

        for brain in brains:
            obj = brain.getObject()
            info = dict(
                title = brain.Title,
                icon = brain.Description.strip().replace('fa-', ''),
                text = obj.getText()
            )

            related = [x for x in obj.getRelatedItems() if x]
            info['URL'] = related[0].absolute_url() if related else None

            results.append(info)

        results = self.grouper(3, results, None)

        return results

    def grouper(self, n, iterable, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

class ZipExhausted(Exception):
    pass

def izip_longest(*args, **kwds):
    # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    fillvalue = kwds.get('fillvalue')
    counter = [len(args) - 1]
    def sentinel():
        if not counter[0]:
            raise ZipExhausted
        counter[0] -= 1
        yield fillvalue
    fillers = itertools.repeat(fillvalue)
    iterators = [itertools.chain(it, sentinel(), fillers) for it in args]
    try:
        while iterators:
            yield tuple(map(next, iterators))
    except ZipExhausted:
        pass

