"""Definition of the Video content type
"""
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import document, schemata
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform
from Products.CMFCore import permissions
from umanot.article.config import PROJECTNAME
from umanot.article.interfaces.video import IVideo

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi

VideoSchema = document.ATDocumentSchema.copy() + atapi.Schema(( #@UndefinedVariable
    atapi.TextField(
        name = 'embed',
        storage = atapi.AnnotationStorage(migrate=True),
        languageIndependent = True,
        widget = atapi.TextAreaWidget(
            label = u"Codice di incorporamento",
        )
    )
))


VideoSchema['title'].storage = atapi.AnnotationStorage()
VideoSchema['title'].required = True
VideoSchema['description'].storage = atapi.AnnotationStorage()
VideoSchema['text'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

imageField = ATImageSchema['image'].copy()
imageField.required = False
imageField.primary = False
imageField.validators = None

VideoSchema.addField(imageField)

schemata.finalizeATCTSchema(VideoSchema, folderish=False, moveDiscussion=False)


class Video(document.ATDocument, ATCTImageTransform):
    """A video file with screenshot"""
    implements(IVideo)

    meta_type = "Video"
    schema = VideoSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                scalename.replace(".jpg", "")
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return document.ATDocument.__bobo_traverse__(self, REQUEST, name)

    def getInfo(self, scale='large', width=None, height=None, mode='crop', css_class=None):
        image = self.getImage()
        has_image = False
        if image:
            has_image = True
            if width and height:
                if mode == 'crop':
                    nu_width, nu_height = self.scale_crop(image.width, image.height, width, height)
                    image = self.tag(scale=scale, width=nu_width, height=nu_height, css_class=css_class)
            else:
                image = self.tag(scale=scale)
        else:
            image = '<img src="default_video.jpg" alt="Sellaronda Hero" />'

        info = dict(
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
            image = image,
            splash = image,
            embed = self.getRawEmbed().strip(),
            has_image = has_image
        )

        return info

atapi.registerType(Video, PROJECTNAME)
