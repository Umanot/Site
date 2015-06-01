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

        import pdb; pdb.set_trace()

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
            typology = self.request.form.get('type'),
            email = self.request.form['email'],
            firstname = self.request.form['firstname'],
            lastname = self.request.form['lastname'],
            fullname = '%s %s' % (self.request.form.get('firstname'), self.request.form.get('lastname')),
            notes = self.request.form.get('notes', ''),
            member = not mtool.isAnonymousUser()
        )

        fullname = sqldata['firstname'] + ' ' + sqldata['lastname']

        self.context.plone_log("Following: %s" % str(self.request.form))

        area = self.umanot_utils.get_area_from_context(self.context)
        if area:
            sqldata['area_title'] = area.Title()
            sqldata['area_uid'] = area.UID()
        else:
            sqldata['area_title'] = 'NULL'
            sqldata['area_uid'] = 'NULL'

        sqldata = self.umanot_utils.prepare_data_for_query(sqldata)
        connection = self.umanot_utils.get_sql_connection(self.request.get('URL'))
        cursor = connection.cursor()

        query = """SELECT id FROM Followers WHERE ContentUID='%(uid)s' AND Typology='%(typology)s' AND Email='%(email)s'""" % sqldata

        records = cursor.execute(query)

        if records:
            return

        query = """INSERT INTO Followers
                (Website, AreaUID, AreaTitle, ContentUID, ContentTitle, Firstname, Lastname, Email, Notes, Typology, Member, Created)
            VALUES
                ('umanot', '%(area_uid)s', '%(area_title)s', '%(uid)s', '%(title)s', '%(firstname)s', '%(lastname)s', '%(email)s', '%(notes)s','%(typology)s', %(member)s,  NOW())""" % sqldata

        cursor.execute(query)
        connection.close()

        # set cookie
        data_string = '%s||%s||%s' % (sqldata['lastname'], sqldata['firstname'], sqldata['email'])
        new_cookie = base64.b64encode(data_string)
        expires = (datetime.datetime.now() + datetime.timedelta(60)).strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        response.setCookie('umanotfollow', '%s' % new_cookie, path = '/', expires = '%s' % expires)

        # notifica via mail
        subject = "[Umanot] Nuovo follower"

        message = '<p>Nuovo follower per: <a href="%s">%s</a></p><br />' % (self.context.absolute_url(), self.context.Title())
        message += "<table>"
        message += '<tr><td width="35%%"><strong>Nome</strong></td><td>%s</td></tr>' % sqldata['fullname']
        message += "<tr><td><strong>Email</strong></td><td>%s</td></tr>" % sqldata['email']
        message += "<tr><td><strong>Note</strong></td><td>%s</td></tr>" % sqldata['notes']
        message += "</table>"
        message += "<hr />"

        if sqldata.get('email') in ['francesco@mediatria.com', 'fsaviano@gmail.com']:
            emails = ['francesco@mediatria.com']
        else:
            emails = ['francesco@mediatria.com']

        for email in emails:
            info = dict(
                receiver = email,
                subject = subject,
                message = message,
            )

            self.umanot_utils.notifySingleUser(info)

        if fullname:
            redirect = '%s?thanks=1&fullname=%s' % (self.context.absolute_url(), fullname)
        else:
            redirect = '%s?thanks=1' % self.context.absolute_url()

        return response.redirect(redirect)