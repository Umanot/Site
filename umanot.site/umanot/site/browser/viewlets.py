from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets import common
from plone.app.layout.viewlets import content
from datetime import date

from plone.app.portlets.portlets import navigation

## LOGO
from umanot.site.browser.interfaces import IAbout, IIntelligenzaConnettiva


class LogoViewlet(common.LogoViewlet):
    index = ViewPageTemplateFile('viewlets/logo.pt')

## SECTIONS
class GlobalSectionsViewlet(common.GlobalSectionsViewlet):
    index = ViewPageTemplateFile('viewlets/sections.pt')

## PERSONALBAR
class PersonalBarViewlet(common.PersonalBarViewlet):
    index = ViewPageTemplateFile('viewlets/personal_bar.pt')

## SEARCHBOX
class SearchBoxViewlet(common.SearchBoxViewlet):
    index = ViewPageTemplateFile('viewlets/searchbox.pt')

## BREADCRUMBS
class PathBarViewlet(common.PathBarViewlet):
    index = ViewPageTemplateFile('viewlets/path_bar.pt')

## BYLINE
class DocumentBylineViewlet(content.DocumentBylineViewlet):
    index = ViewPageTemplateFile("viewlets/document_byline.pt")

## DOCUMENT ACTIONS
class DocumentActionsViewlet(content.DocumentActionsViewlet):
    index = ViewPageTemplateFile("viewlets/document_actions.pt")

## RELATED ITEMS
class ContentRelatedItems(content.ContentRelatedItems):
    index = ViewPageTemplateFile("viewlets/document_relatedItems.pt")

## SITEACTIONS 
class SiteActionsViewlet(common.SiteActionsViewlet):
    index = ViewPageTemplateFile('viewlets/site_actions.pt')

## FOOTER 
class FooterViewlet(common.FooterViewlet):
    index = ViewPageTemplateFile('viewlets/footer.pt')

    def update(self):
        super(FooterViewlet, self).update()
        self.year = date.today().year

    def about(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(
            portal_type = "Document",
            object_provides = IAbout.__identifier__
        )

        if not brains:
            return

        brain = brains[0]

        info = dict(
            title = brain.Title,
            description = brain.Description,
            URL = brain.getURL()
        )

        return info

    def articles(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        folders = catalog(
            portal_type = "Folder",
            object_provides = IIntelligenzaConnettiva.__identifier__
        )

        if not folders:
            return

        folder = folders[0]

        brains = catalog(
            portal_type = ["Article", "Placeholder"],
            path = folder.getPath(),
            sort_on = 'Date',
            sort_order = 'reverse'
        )

        results = []

        for brain in brains:
            obj = brain.getObject()
            info = obj.getInfo()

            results.append(info)

        return results
        
## COLOPHON 
class ColophonViewlet(ViewletBase):
    index = ViewPageTemplateFile('viewlets/colophon.pt')

    def update(self):
        self.year = date.today().year


## NAVIGATION Portlet
class Renderer(navigation.Renderer):

    _template = ViewPageTemplateFile('portlets/navigation.pt')
    recurse = ViewPageTemplateFile('portlets/navigation_recurse.pt')