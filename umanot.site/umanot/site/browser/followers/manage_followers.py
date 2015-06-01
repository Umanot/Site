from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.interface import implements, Interface
from zope.component import getMultiAdapter, getUtility

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class IManageFollowersView(Interface):
    """
    FollowThanks view interface
    """


class ManageFollowersView(BrowserView):
    """
    FollowThanks browser view
    """
    implements(IManageFollowersView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.plone_view = getMultiAdapter((self.context, self.request), name = u'plone')
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.umanot_utils = getUtility(IUmanotUtils)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()

    @property
    def followers(self):
        fields = ('AreaUID', 'AreaTitle', 'ContentUID', 'ContentTitle', 'Firstname', 'Lastname', 'Email', 'Typology', 'Member')

        sqldata = dict(
            fields = fields,
        )

        sqldata = self.umanot_utils.prepare_data_for_query(sqldata)
        connection = self.umanot_utils.get_sql_connection(self.request.get('URL'))
        cursor = connection.cursor()

        query = """SELECT %(fields)s FROM Followers WHERE website='umanot'""" % sqldata

        records = cursor.execute(query)
        connection.close()

        results = []
        contents = {}
        contents_and_area_map = {}

        for record in records:
            tmp = dict(zip(fields, record))
            
            if tmp['ContentUID'] not in contents:
                contents_and_area_map[tmp['ContentUID']] = tmp['ContentTitle']
                if tmp['AreaUID']:
                    contents_and_area_map[tmp['AreaUID']] = tmp['AreaTitle']

                contents[tmp['ContentUID']] = []

            contents[tmp['ContentUID']].append(tmp)

        for x in contents:
            pass

        return results
