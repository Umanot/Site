# -*- coding: utf-8 -*-
"""Definition of the Placeholder content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import document, schemata
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform
from Products.Archetypes import atapi
from Products.CMFCore import permissions
import requests
from umanot.article.config import PROJECTNAME
from umanot.article.interfaces.placeholder import IPlaceholder
from zope.interface import implements


PlaceholderSchema = document.ATDocumentSchema.copy() + atapi.Schema((
    atapi.StringField(
        name = 'clab_uid',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"ID ComplexLab",
        ),
    )
))

PlaceholderSchema['title'].storage = atapi.AnnotationStorage()
PlaceholderSchema['title'].required = True
PlaceholderSchema['description'].storage = atapi.AnnotationStorage()

imageField = ATImageSchema['image'].copy()
imageField.required = False
imageField.primary = False
imageField.validators = None

PlaceholderSchema.addField(imageField)

PlaceholderSchema.moveField('text', after = 'description')
PlaceholderSchema.moveField('image', after = 'text')

schemata.finalizeATCTSchema(PlaceholderSchema, folderish = False, moveDiscussion = False)

PlaceholderSchema['text'].widget.visible = {'edit': 'hidden', 'view': 'hidden'}
PlaceholderSchema['relatedItems'].widget.visible = {'edit': 'visible', 'view': 'visible'}

class Placeholder(document.ATDocument, ATCTImageTransform):
    """The product unit content type"""
    implements(IPlaceholder)

    meta_type = "Placeholder"
    schema = PlaceholderSchema

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
                    image = field.getScale(self, scale = scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return document.ATDocument.__bobo_traverse__(self, REQUEST, name)

    def getInfo(self, scale='large', width=None, height=None, mode='crop', css_class=None):
        image = self.getImage()

        url = 'http://www.complexlab.it/api'
        params = {'page': 'article', 'uid': self.getClab_uid()}
        remote_data = requests.get(url, params=params)

        remote_info = remote_data.json()

        if image:
            if width and height:
                if mode == 'crop':
                    nu_width, nu_height = self.scale_crop(image.width, image.height, width, height)
                    image = self.tag(scale = scale, width = nu_width, height = nu_height, css_class = css_class)
            elif scale == "original":
                image = self.tag()
            else:
                image = self.tag(scale = scale)
        else:
            self.plone_log("Syncing image for: %s" % self.absolute_url())
            if remote_info['image']:
                self.syncImage(remote_info['URL'])

        info = dict(
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
            text = remote_info['text'],
            image = image,
            autore = '',
        )

        return info

    def syncImage(self, url):
        image_url = '%s/image' % url
        self.plone_log(" -> %s" % image_url)
        if image_url:
            image_response = requests.get(image_url, stream=True)
            image_response.raw.decode_content = True
            self.setImage(image_response.raw.data)
            self.plone_log("Image succesfully set for: %s" % self.absolute_url())


atapi.registerType(Placeholder, PROJECTNAME)