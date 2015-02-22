# -*- coding: utf-8 -*-
"""Definition of the Slide content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import document, schemata
from Products.ATContentTypes.content.image import ATImageSchema
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from toshibaclima.homepage.config import PROJECTNAME, TEXT_POSITIONS
from toshibaclima.homepage.interfaces.slide import ISlide
from zope.interface import implements
try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
    

SlideSchema = document.ATDocumentSchema.copy() + atapi.Schema(( #@UndefinedVariable
    atapi.ReferenceField(
        name = 'link',
        multiValued = False,
        relationship = 'link_in_slide',
        keepReferencesOnCopy = True,
        widget=ReferenceBrowserWidget(
            label = u"Elemento collegato",
            allow_search=1,
            allow_browse=1,
            show_indexes=0,
        ),
    ),
    atapi.StringField(
        name = 'text_position',
        storage = atapi.AnnotationStorage(),
        languageIndependent = True,
        vocabulary = 'getTextPostions',
        widget = atapi.SelectionWidget(
            label = u"Posizione del testo",
            format = 'select'
        ),
    ),
))

SlideSchema['title'].storage = atapi.AnnotationStorage()
SlideSchema['title'].required = 1
SlideSchema['title'].searchable = 0
SlideSchema['description'].storage = atapi.AnnotationStorage()
SlideSchema['description'].required = 0
SlideSchema['description'].searchable = 0
SlideSchema['description'].widget.label = "Testo grande"
SlideSchema['description'].widget.label_msgid = "Testo grande"
SlideSchema['text'].widget.label = "Testo piccolo"
SlideSchema['text'].widget.label_msgid = "Testo piccolo"

imageField = ATImageSchema['image'].copy()
imageField.required = False
imageField.primary = False
imageField.validators = None

SlideSchema.addField(imageField)

SlideSchema.moveField('image', after='text')

schemata.finalizeATCTSchema(SlideSchema)

class Slide(document.ATDocument):
    """The Slide item"""
    
    implements(ISlide)

    portal_type = "Slide"
    schema = SlideSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    def getTextPostions(self):
        return DisplayList(TEXT_POSITIONS)
    
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
    
    def getInfo(self, scale='mini', width=None, height=None, mode='crop', css_class=None):
        """The Slide main informations"""
            
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
        
        url = ''
        link = self.getLink()
        external = False
        if link:
            url = link.getRemoteUrl() if link.portal_type == 'Link' else link.absolute_url()
            external = link.portal_type == 'Link'
            
        css_class = 'cellHeadline'
        text_position = self.getText_position()
        if text_position == 'left':
            css_class += ' positionLeft'
        elif text_position == 'right':
            css_class += ' positionRight'
        else:
            css_class += ' positionCenter'
            
        info = dict(
            uid = self.UID(),
            title = self.Title(),
            description = self.Description(),
            text = self.getText(),
            URL = url,
            image = image,
            external = external,
            css_class = css_class
        )
        
        return info
    
atapi.registerType(Slide, PROJECTNAME)