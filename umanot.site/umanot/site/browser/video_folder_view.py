import itertools
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IVideoFolderView(Interface):
    """
    Video Folder view interface
    """


class VideoFolderView(BrowserView):
    """
    Video Folder  browser view
    """
    implements(IVideoFolderView)

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
            portal_type = "Video",
            path = '/'.join(self.context.getPhysicalPath()),
            sort_on = 'getObjPositionInParent'
        )

        results = []

        for brain in brains:
            obj = brain.getObject()
            info = obj.getInfo(scale="preview", width=300, height=-1)

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
        