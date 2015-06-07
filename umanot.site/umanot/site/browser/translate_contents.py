from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import implements, Interface

TYPES_WHITE_LIST = ['Folder', 'Image']


class ITranslateContentsView(Interface):
    """
    TranslateContents view interface
    """


class TranslateContentsView(BrowserView):
    """
    TranslateContents browser view
    """
    implements(ITranslateContentsView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.language = request.get('LANGUAGE')
        self.dig = request.get('dig', True)

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        query = dict(
            portal_type = TYPES_WHITE_LIST,
        )

        if self.dig:
            query['path'] = '/'.join(self.context.getPhysicalPath())
        else:
            query['path'] = {'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1}

        brains = catalog(query)

        processed = 0

        langs = [x for x in self.getLanguages() if x != self.language]

        totals = len(brains)

        brains = [x for x in brains]

        # we sort brains on path length so we always start translating from the container
        brains.sort(lambda x, y: cmp(len(x.getPath().split('/')), len(y.getPath().split('/'))))

        # link already present same id content if not linked

        for brain in brains:
            processed += 1
            self.context.plone_log('Processing [%s] %s of %s' % (brain.Title, processed, totals))
            obj = brain.getObject()

            for lang in langs:
                if not obj.hasTranslation(lang):

                    # if we have same ids in translated parent we link them
                    # we consider this lika a precondition
                    parent = obj.aq_parent
                    if parent.hasTranslation(lang):
                        translated_parent = parent.getTranslation(lang)
                        obj_id = obj.getId()
                        if obj_id in translated_parent.keys():
                            translation = getattr(translated_parent, obj_id)
                            obj.linkTranslation(link_language = lang, link_content = translation.UID())
                            self.context.plone_log("--> linking %s for %s" % (obj_id, lang))
                            continue

                    # else we simply create new language content
                    self.context.plone_log("--> %s creating" % lang)
                    translated = obj.addTranslation(lang)

                    translated.setTitle(obj.Title())
                    translated.reindexObject()
                else:
                    self.context.plone_log("--> %s already exists" % lang)

        IStatusMessage(self.request).addStatusMessage(u"Immagini tradotte correttamente", type = 'info')
        response = self.request.RESPONSE
        return response.redirect(self.context.absolute_url())

    def getLanguages(self):
        """
        Return list of active langauges as ordered dictionary, the preferred first language as the first.

        Example output::

             {
                u'fi': {u'id' : u'fi', u'flag': u'/++resource++country-flags/fi.gif', u'name': u'Finnish', u'native': u'Suomi'},
                u'de': {u'id' : u'de', u'flag': u'/++resource++country-flags/de.gif', u'name': u'German', u'native': u'Deutsch'},
                u'en': {u'id' : u'en', u'flag': u'/++resource++country-flags/gb.gif', u'name': u'English', u'native': u'English'},
                u'ru': {u'id' : u'ru', u'flag': u'/++resource++country-flags/ru.gif', u'name': u'Russian', u'native': u'\u0420\u0443\u0441\u0441\u043a\u0438\u0439'}
              }
        """
        result = {}

        portal_languages = self.context.portal_languages

        # Get barebone language listing from portal_languages tool
        langs = portal_languages.getAvailableLanguages()

        preferred = portal_languages.getPreferredLanguage()

        # Preferred first
        for lang, data in langs.items():
            if lang == preferred:
                result[lang] = data

        # Then other languages
        for lang, data in langs.items():
            if lang != preferred:
                result[lang] = data

        # For convenience, include the language ISO code in the export,
        # so it is easier to iterate data in the templates
        for lang, data in result.items():
            data["id"] = lang

        return result
