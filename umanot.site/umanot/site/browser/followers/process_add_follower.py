# -*- coding: utf-8 -*-
import base64
from Products.CMFCore.utils import getToolByName
from umanot.site.browser.umanot_utils import IUmanotUtils
from zope.component import getUtility

from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
import datetime
import oursql


class IProcessAddFollower(Interface):
    """
    ProcessAddFollower view interface
    """


class ProcessAddFollower(BrowserView):
    """
    ProcessAddFollower browser view
    """
    implements(IProcessAddFollower)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.umanot_utils = getUtility(IUmanotUtils)

    def __call__(self):
        request = self.request
        response = request.RESPONSE

        required = ['firstname', 'lastname', 'email']

        errors = {}

        if errors:
            self.request.form['fw-errors'] = errors
            for k, v in self.request.form.iteritems():
                self.request.form[k] = v

            IStatusMessage(self.request).addStatusMessage(u"Correggi gli errori evidenziati", type = 'error')
            return self.context.restrictedTraverse('@@add-follower-page')()

        mtool = getToolByName(self.context, 'portal_membership')
        sqldata = dict(
            uid = self.context.UID(),
            title = self.context.Title(),
            typology = self.request.form.get('typology'),
            email = self.request.form['email'],
            firstname = self.request.form['firstname'],
            lastname = self.request.form['lastname'],
            notes = self.request.form.get('notes', ''),
            member = not mtool.isAnonymousUser()
        )

        fullname = sqldata['firstname'] + ' ' + sqldata['lastname']

        self.context.plone_log("Following: %s" % str(self.request.form))

        import pdb; pdb.set_trace()

        area = self.umanot_utils.get_area_from_context(self.context)
        if area:
            sqldata['area_title'] = area.Title()
            sqldata['area_uid'] = area.UID()
        else:
            sqldata['area_title'] = 'NULL'
            sqldata['area_uid'] = 'NULL'

        connection = self.umanot_utils.get_sql_connection(self.request.get('URL'))
        cursor = connection.cursor()

        query = """SELECT id FROM Followers WHERE ContentUID='%(uid)s' AND Typology='%(typology)s' AND Email='%(email)s'""" % sqldata

        records = cursor.execute(query)

        if records:
            return

        cursor.execute("""INSERT INTO Followers
                (Website, AreaUID, AreaTitle, ContentUID, ContentTitle, Firstname, Lastname, Email, Notes, Typology, Member, Created)
            VALUES
                ('umanot', '%(area_uid)s', '%(area_title)s', '%(uid)s', '%(title)s', '%(firstname)s', '%(lastname)s', '%(email)s', '%(notes)s','%(typology)s', %(member)s,  NOW()))""" % sqldata)

        # set cookie
        data_string = '%s||%s||%s' % (sqldata['lastname'], sqldata['firstname'], sqldata['email'])
        new_cookie = base64.b64encode(data_string)
        expires = (datetime.datetime.now() + datetime.timedelta(60)).strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        response.setCookie('umanotfollow', '%s' % new_cookie, path = '/', expires = '%s' % expires)

        if fullname:
            redirect = '%s/@@follow-thanks?fullname=%s' % (self.context.absolute_url(), fullname)
        else:
            redirect = '%s/@@follow-thanks' % self.context.absolute_url()

        return response.redirect(redirect)