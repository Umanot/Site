from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IPartnerFolderView(Interface):
    """
    Partner Folder view interface
    """


class PartnerFolderView(BrowserView):
    """
    Partner Folder browser view
    """
    implements(IPartnerFolderView)

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
            portal_type = "Image",
            path = '/'.join(self.context.getPhysicalPath()),
            sort_on = 'getObjPositionInParent'
        )

        results = []

        for brain in brains:
            obj = brain.getObject()

            image = obj.getImage()
            nu_width, nu_height = self.context.scale_crop(image.width, image.height, -1, 100)
            image_markup = obj.tag(scale = 'preview', width = nu_width, height = nu_height, css_class = 'img-responsive')

            info = dict(
                title = brain.Title,
                description = brain.Description,
                URL = brain.getURL(),
                image = image_markup
            )

            results.append(info)

        return results
        