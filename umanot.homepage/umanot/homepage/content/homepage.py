# -*- coding: utf-8 -*-
"""Definition of the Homepage content type
"""
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content import folder, schemata
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.image import ATImageSchema
from Products.CMFCore import permissions
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from umanot.homepage.config import PROJECTNAME
from umanot.homepage.interfaces.homepage import IHomepage

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi

HomepageSchema = folder.ATFolderSchema.copy() + atapi.Schema(
    (
        atapi.ReferenceField(
            name = 'slides',
            multiValued = True,
            relationship = 'slides_in_homepage',
            keepReferencesOnCopy = True,
            widget = ReferenceBrowserWidget(
                label = u"Slide",
                allow_search = 1,
                allow_browse = 1,
                show_indexes = 0,
                base_query = {'portal_type': 'Slide'},
            ),
        ),
        atapi.StringField(
            name = 'box1_title',
            required = 0,
            searchable = 0,
            schemata = 'Box 1',
            storage = atapi.AnnotationStorage(),
            widget = atapi.StringWidget(
                label = u'Titolo',
                description = 'Il titolo del primo box',
            ),
        ),
        atapi.TextField(
            name = 'box1_text',
            searchable = 0,
            schemata = 'Box 1',
            storage = atapi.AnnotationStorage(),
            validators = ('isTidyHtmlWithCleanup',),
            default_output_type = 'text/x-html-safe',
            widget = atapi.RichWidget(
                label = u'Text',
                description = "",
                rows = 20,
            ),
        ),
        atapi.ImageField(
            name = "box1_image",
            storage = atapi.AnnotationStorage(migrate = True),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,  # @UndefinedVariable
            schemata = 'Box 1',
            sizes = {"large": (768, 768),
                     "preview": (400, 400),
                     "mini": (200, 200),
                     "thumb": (128, 128),
                     "tile": (64, 64),
                     "icon": (32, 32),
            },
            widget = atapi.ImageWidget(
                label = "Immagine",
            ),
        ),
        atapi.ReferenceField(
            name = 'box1_link',
            multiValued = False,
            relationship = 'box1_link_in_home',
            keepReferencesOnCopy = True,
            schemata = 'Box 1',
            widget = ReferenceBrowserWidget(
                label = u"Contenuto collegato",
                allow_search = 1,
                allow_browse = 1,
                show_indexes = 0,
                startup_directory = '.'
            ),
        ),
        atapi.StringField(
            name = 'box2_title',
            required = 0,
            searchable = 0,
            schemata = 'Box 2',
            storage = atapi.AnnotationStorage(),
            widget = atapi.StringWidget(
                label = u'Titolo',
                description = 'Il titolo del primo box',
            ),
        ),
        atapi.TextField(
            name = 'box2_text',
            searchable = 0,
            schemata = 'Box 2',
            storage = atapi.AnnotationStorage(),
            validators = ('isTidyHtmlWithCleanup',),
            default_output_type = 'text/x-html-safe',
            widget = atapi.RichWidget(
                label = u'Text',
                description = "",
                rows = 20,
            ),
        ),
        atapi.ImageField(
            name = "box2_image",
            storage = atapi.AnnotationStorage(migrate = True),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,  # @UndefinedVariable
            schemata = 'Box 2',
            sizes = {"large": (768, 768),
                     "preview": (400, 400),
                     "mini": (200, 200),
                     "thumb": (128, 128),
                     "tile": (64, 64),
                     "icon": (32, 32),
            },
            widget = atapi.ImageWidget(
                label = "Immagine",
            ),
        ),
        atapi.ReferenceField(
            name = 'box2_link',
            multiValued = False,
            relationship = 'box2_link_in_home',
            keepReferencesOnCopy = True,
            schemata = 'Box 2',
            widget = ReferenceBrowserWidget(
                label = u"Contenuto collegato",
                allow_search = 1,
                allow_browse = 1,
                show_indexes = 0,
                startup_directory = '.'
            ),
        ),
        atapi.StringField(
            name = 'box3_title',
            required = 0,
            searchable = 0,
            schemata = 'Box 3',
            storage = atapi.AnnotationStorage(),
            widget = atapi.StringWidget(
                label = u'Titolo',
                description = 'Il titolo del primo box',
            ),
        ),
        atapi.TextField(
            name = 'box3_text',
            searchable = 0,
            schemata = 'Box 3',
            storage = atapi.AnnotationStorage(),
            validators = ('isTidyHtmlWithCleanup',),
            default_output_type = 'text/x-html-safe',
            widget = atapi.RichWidget(
                label = u'Text',
                description = "",
                rows = 20,
            ),
        ),
        atapi.ImageField(
            name = "box3_image",
            storage = atapi.AnnotationStorage(migrate = True),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,  # @UndefinedVariable
            schemata = 'Box 3',
            sizes = {"large": (768, 768),
                     "preview": (400, 400),
                     "mini": (200, 200),
                     "thumb": (128, 128),
                     "tile": (64, 64),
                     "icon": (32, 32),
            },
            widget = atapi.ImageWidget(
                label = "Immagine",
            ),
        ),
        atapi.ReferenceField(
            name = 'box3_link',
            multiValued = False,
            relationship = 'box3_link_in_home',
            keepReferencesOnCopy = True,
            schemata = 'Box 3',
            widget = ReferenceBrowserWidget(
                label = u"Contenuto collegato",
                allow_search = 1,
                allow_browse = 1,
                show_indexes = 0,
                startup_directory = '.'
            ),
        ),
        atapi.TextField(
            name = 'about_footer',
            storage = atapi.AnnotationStorage(),
            schemata = 'Footer',
            widget = atapi.TextAreaWidget(
                label = u"Perché noi (footer)"
            )
        )
    )
)

HomepageSchema['title'].storage = atapi.AnnotationStorage()
HomepageSchema['title'].required = 1
HomepageSchema['title'].searchable = 0
HomepageSchema['description'].storage = atapi.AnnotationStorage()
HomepageSchema['description'].required = 0
HomepageSchema['description'].searchable = 0

textField = ATDocumentSchema['text'].copy()
textField.required = False
textField.validators = None

HomepageSchema.addField(textField)

HomepageSchema.moveField('text', after = 'description')

schemata.finalizeATCTSchema(HomepageSchema, folderish = False, moveDiscussion = False)


class Homepage(ATFolder):
    """The Homepage item"""

    implements(IHomepage)

    portal_type = "Homepage"
    schema = HomepageSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security.declareProtected(permissions.View, 'box1ImageTag')

    def box1ImageTag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('box1_image').tag(self, **kwargs)

    security.declareProtected(permissions.View, 'box2ImageTag')

    def box2ImageTag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('box2_image').tag(self, **kwargs)

    security.declareProtected(permissions.View, 'box3ImageTag')

    def box3ImageTag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('box3_image').tag(self, **kwargs)

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('box1_image'):
            field = self.getField('box1_image')
            image = None
            if name == 'box1_image':
                image = field.getScale(self)
            else:
                scalename = name[len('box1_image_'):]
                scalename.replace(".jpg", "")
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale = scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image
        elif name.startswith('box2_image'):
            field = self.getField('box2_image')
            image = None
            if name == 'box2_image':
                image = field.getScale(self)
            else:
                scalename = name[len('box2_image_'):]
                scalename.replace(".jpg", "")
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale = scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image
        elif name.startswith('box3_image'):
            field = self.getField('box3_image')
            image = None
            if name == 'box3_image':
                image = field.getScale(self)
            else:
                scalename = name[len('box3_image_'):]
                scalename.replace(".jpg", "")
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale = scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return folder.ATFolder.__bobo_traverse__(self, REQUEST, name)

    def getInfo(self):
        """The Slide main informations"""

        width = 272
        height = -1

        box1_image = self.getBox1_image()

        if box1_image:
            nu_width, nu_height = self.scale_crop(box1_image.width, box1_image.height, width, height)
            box1_image = self.box1ImageTag(scale = 'preview', width = nu_width, height = nu_height)

        box1_link = self.getBox1_link()
        box1_external = False
        if box1_link:
            box1_external = box1_link.portal_type == 'Link'
            box1_link = box1_link.getRemoteUrl() if box1_link.portal_type == 'Link' else box1_link.absolute_url()

        box2_image = self.getBox2_image()

        if box2_image:
            nu_width, nu_height = self.scale_crop(box2_image.width, box2_image.height, width, height)
            box2_image = self.box2ImageTag(scale = 'preview', width = nu_width, height = nu_height)

        box2_link = self.getBox2_link()
        box2_external = False
        if box2_link:
            box2_external = box2_link.portal_type == 'Link'
            box2_link = box2_link.getRemoteUrl() if box2_link.portal_type == 'Link' else box2_link.absolute_url()

        box3_image = self.getBox3_image()

        if box3_image:
            nu_width, nu_height = self.scale_crop(box3_image.width, box3_image.height, width, height)
            box3_image = self.box3ImageTag(scale = 'preview', width = nu_width, height = nu_height)

        box3_link = self.getBox3_link()
        box3_external = False
        if box3_link:
            box3_external = box3_link.portal_type == 'Link'
            box3_link = box3_link.getRemoteUrl() if box3_link.portal_type == 'Link' else box3_link.absolute_url()

        slides_uids = self.getRawSlides()
        slides = [x.getObject() for x in self.portal_catalog(UID = slides_uids)]

        info = dict(
            uid = self.UID(),
            title = self.Title(),
            description = self.Description(),
            text = self.getText(),
            URL = self.absolute_url(),
            slides = [x.getInfo(scale = "original") for x in slides],
            box1_title = self.getBox1_title(),
            box1_text = self.getBox1_text(),
            box1_image = box1_image,
            box1_link = box1_link,
            box1_external = box1_external,
            box2_title = self.getBox2_title(),
            box2_text = self.getBox2_text(),
            box2_image = box2_image,
            box2_link = box2_link,
            box2_external = box2_external,
            box3_title = self.getBox3_title(),
            box3_text = self.getBox3_text(),
            box3_image = box3_image,
            box3_link = box3_link,
            box3_external = box3_external,
        )

        return info


atapi.registerType(Homepage, PROJECTNAME)