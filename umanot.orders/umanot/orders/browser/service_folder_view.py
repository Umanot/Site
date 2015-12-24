import itertools

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

    def get_placeholder_text(self):
        try:
            intro = self.context.restrictedTraverse('/umanot/it/listino-servizi/intro')
        except:
            intro = ''

        try:
            footer = self.context.restrictedTraverse('/umanot/it/listino-servizi/footer')
        except:
            footer = ''

        info = dict(
            intro = intro.getText() if intro else '',
            footer = footer.getText() if footer else ''
        )

        return info


    @property
    def contents(self):
        brains = self.portal_catalog(
            portal_type = "Folder",
            path = {'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
            sort_on = 'getObjPositionInParent'
        )

        results = []

        for brain in brains:
            if brain.exclude_from_nav:
                continue

            info = dict(
                id = brain.getId,
                title = brain.Title,
                description = brain.Description,
            )

            contents = self.portal_catalog(
                portal_type = "Product",
                path = brain.getPath(),
                sort_on = 'getObjPositionInParent'
            )

            info['contents'] = []
            for x in contents:
                sub = dict(
                    title = x.Title,
                    description = x.Description,
                    URL = x.getURL()
                )
                info['contents'].append(sub)

            if info['contents']:
                info['contents'] = self.grouper(4, info['contents'], None)
            else:
                continue

            results.append(info)

        return results

    def grouper(self, n, iterable, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue = fillvalue, *args)


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
