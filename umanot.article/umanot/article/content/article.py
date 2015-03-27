# -*- coding: utf-8 -*-
"""Definition of the Article content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import folder, schemata
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from umanot.article.config import PROJECTNAME
from umanot.article.interfaces.article import IArticle
from zope.interface import implements


ArticleSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.StringField(
        name = 'autore',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Autore",
        )
    )
    # atapi.TextField(
    #     name = 'video',
    #     storage = atapi.AnnotationStorage(),
    #     languageIndependent = False,
    #     widget = atapi.TextAreaWidget(
    #         label = u"Video",
    #     ),
    # ),
))

ArticleSchema['title'].storage = atapi.AnnotationStorage()
ArticleSchema['title'].required = True
ArticleSchema['description'].storage = atapi.AnnotationStorage()

textField = ATDocumentSchema['text'].copy()
textField.required = False
textField.validators = None

ArticleSchema.addField(textField)

imageField = ATImageSchema['image'].copy()
imageField.required = False
imageField.primary = False
imageField.validators = None

ArticleSchema.addField(imageField)

ArticleSchema.moveField('text', after='description')
ArticleSchema.moveField('image', after='text')

schemata.finalizeATCTSchema(ArticleSchema, folderish=False, moveDiscussion=False)

ArticleSchema['relatedItems'].widget.visible = {'edit': 'visible', 'view': 'visible'}

class Article(folder.ATFolder, ATCTImageTransform):
    """The product unit content type"""
    implements(IArticle)

    meta_type = "Article"
    schema = ArticleSchema

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

        return folder.ATFolder.__bobo_traverse__(self, REQUEST, name)

    def getInfo(self, scale='large', width=None, height=None, mode='crop', css_class=None):
        image = self.getImage()

        if image:
            if width and height:
                if mode == 'crop':
                    nu_width, nu_height = self.scale_crop(image.width, image.height, width, height)
                    image = self.tag(scale=scale, width=nu_width, height=nu_height, css_class=css_class)
            elif scale == "original":
                image = self.tag()
            else:
                image = self.tag(scale=scale)

        info = dict(
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
            text = self.getText(),
            image = image,
            # video = self.getRawVideo().strip(),
        )

        return info

atapi.registerType(Article, PROJECTNAME)