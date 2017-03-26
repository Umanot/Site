# -*- coding: utf-8 -*-
"""Definition of the Post content type
"""
from AccessControl import ClassSecurityInfo
from DateTime.DateTime import DateTime
from Products.ATContentTypes.content import folder, schemata
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.image import ATImageSchema
from Products.ATContentTypes.lib.imagetransform import ATCTImageTransform

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from mediatria.utils.browser.mediatria_utils import IMediatriaUtils
from umanot.article.config import PROJECTNAME
from umanot.article.interfaces.post import IPost
from zope.component import getUtility
from zope.interface import implements


PostSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.StringField(
        name = 'titolo',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Titolo",
        )
    ),
    atapi.StringField(
        name = 'intervallo',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Intervallo dati",
        )
    ),
    atapi.StringField(
        name = 'operazioni',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Operazioni",
        )
    ),
    atapi.StringField(
        name = 'operazioni_12',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Operazioni in profitto / perdita",
        )
    ),
    atapi.StringField(
        name = 'operazioni_1x2',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Operazioni in profitto / perdita / pareggio",
        )
    ),
    atapi.StringField(
        name = 'operazioni_1x3',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Net profitto",
        )
    ),
    atapi.StringField(
        name = 'metodologia',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Metodologia",
        )
    ),
    atapi.StringField(
        name = 'software',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Software",
        )
    ),
    atapi.TextField(
        name = 'notes',
        storage = atapi.AnnotationStorage(),
        widget = atapi.TextAreaWidget(
            label = u"Note",
        )
    ),
    atapi.TextField(
        name = 'importante',
        storage = atapi.AnnotationStorage(),
        widget = atapi.RichWidget(
            label = u"Importante",
            rows = 12,
        ),
    )
))

PostSchema['title'].storage = atapi.AnnotationStorage()
PostSchema['title'].required = True
PostSchema['description'].storage = atapi.AnnotationStorage()

textField = ATDocumentSchema['text'].copy()
textField.required = False
textField.validators = None

PostSchema.addField(textField)

imageField = ATImageSchema['image'].copy()
imageField.required = False
imageField.primary = False
imageField.validators = None

PostSchema.addField(imageField)

PostSchema.moveField('text', after = 'description')
PostSchema.moveField('image', after = 'text')

schemata.finalizeATCTSchema(PostSchema, folderish = False, moveDiscussion = False)

PostSchema['relatedItems'].widget.visible = {'edit': 'visible', 'view': 'visible'}


class Post(folder.ATFolder, ATCTImageTransform):
    """The product unit content type"""
    implements(IPost)

    meta_type = "Post"
    schema = PostSchema

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

        return folder.ATFolder.__bobo_traverse__(self, REQUEST, name)

    def getInfo(self, scale='large', width=None, height=None, mode='crop', css_class=None):
        effective = DateTime(self.Date())
        mediatria_utils = getUtility(IMediatriaUtils)
        effective_readable = "%s %s %s" % (effective.strftime('%d'), mediatria_utils.getMonthName(self, effective.month()), effective.strftime('%Y'))

        image = self.getImage()

        if image:
            if width and height:
                if mode == 'crop':
                    nu_width, nu_height = self.scale_crop(image.width, image.height, width, height)
                    image = self.tag(scale = scale, width = nu_width, height = nu_height, css_class = css_class)
            elif scale == "original":
                image = self.tag()
            else:
                image = self.tag(scale = scale)

        info = dict(
            uid = self.UID(),
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
            text = self.getText(),
            image = image,
            readable_date = effective_readable,
            sortable_date = effective.asdatetime().isoformat(),
            titolo = self.getTitolo(),
            intervallo = self.getIntervallo(),
            operazioni = self.getOperazioni(),
            operazioni_12 = self.getOperazioni_12(),
            operazioni_1x2 = self.getOperazioni_1x2(),
            operazioni_1x3=self.getOperazioni_1x3(),
            metodologia = self.getMetodologia(),
            software = self.getSoftware(),
            notes = self.getNotes(),
            importante = self.getRawImportante(),
        )

        return info

    def other_images(self):
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(
            portal_type = "Image",
            path = '/'.join(self.getPhysicalPath()),
            sort_on = 'getObjPositionInParent',
        )

        results = []

        for brain in brains:
            tag = brain.getObject().tag()
            results.append(tag)

        return results


atapi.registerType(Post, PROJECTNAME)