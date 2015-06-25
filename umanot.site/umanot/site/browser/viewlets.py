import random

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets import common
from plone.app.layout.viewlets import content
from datetime import date
from plone.app.portlets.portlets import navigation


## LOGO
from umanot.site.browser.interfaces import IAbout, IIntelligenzaConnettiva
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility


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

    @property
    def contents(self):
        results = []
        catalog = getToolByName(self.context, 'portal_catalog')
        if self.context.portal_type == "Video":
            brains = catalog(
                portal_type = "Video",
                sort_on = 'getObjPositionInParent'
            )

            context_uid = self.context.UID()

            for brain in brains:
                if brain.UID == context_uid:
                    continue
                obj = brain.getObject()
                info = obj.getInfo()

                results.append(info)

        return results


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

        homepage = catalog(
            portal_type = "Homepage",
        )

        if not brains or not homepage:
            return

        brain = brains[0]

        obj = homepage[0].getObject()

        info = dict(
            title = brain.Title,
            description = obj.getAbout_footer(),
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
            getFooter_featured = True,
            sort_on = 'Date',
            sort_order = 'reverse',
            sort_limit = 3
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


## RELATED 
class RelatedItemsViewlet(ViewletBase):
    index = ViewPageTemplateFile('viewlets/related_items.pt')


## LEADERBOARD TOP 
class LeaderboardTopViewlets(ViewletBase):
    index = ViewPageTemplateFile('viewlets/leaderboard_top.pt')

    def image(self):
        umanot_utils = getUtility(IUmanotUtils)
        context = self.context
        tmp = umanot_utils.getLocalAd(context) or {}
        images = tmp.get('top')

        try:
            while not images:
                context = context.aq_parent
                data = umanot_utils.getLocalAd(context)
                if data and data.get('top'):
                    images = data['top']
        except:
            return

        background = random.choice(images)

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(
            UID = background,
        )

        if not brains:
            return

        brain = brains[0]

        info = dict(
            title = brain.Title,
            remote_url = brain.Description,
            image_url = brain.getURL()
        )

        return info


## LEADERBOARD BOTTOM 
class LeaderboardBottomViewlets(ViewletBase):
    index = ViewPageTemplateFile('viewlets/leaderboard_bottom.pt')

    def image(self):
        umanot_utils = getUtility(IUmanotUtils)
        context = self.context
        tmp = umanot_utils.getLocalAd(context) or {}
        images = tmp.get('bottom')

        try:
            while not images:
                context = context.aq_parent
                data = umanot_utils.getLocalAd(context)
                if data and data.get('bottom'):
                    images = data['bottom']
        except:
            return

        background = random.choice(images)

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(
            UID = background,
        )

        if not brains:
            return

        brain = brains[0]

        info = dict(
            title = brain.Title,
            remote_url = brain.Description,
            image_url = brain.getURL()
        )

        return info


## NAVIGATION Portlet
class Renderer(navigation.Renderer):
    _template = ViewPageTemplateFile('portlets/navigation.pt')
    recurse = ViewPageTemplateFile('portlets/navigation_recurse.pt')
