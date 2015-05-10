# -*- coding: utf-8 -*-
import base64

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

    def __call__(self):
        request = self.request
        response = request.RESPONSE

        import pdb; pdb.set_trace()

        conn = oursql.connect(host='172.16.108.11', user='root', passwd='112d24e2', db='ComplexLab')

        errors = {}
        data = {}

        if errors:
            self.request.form['follow-errors'] = errors
            for data_k, data_v in data.items():
                self.request.form[data_k] = data_v

            IStatusMessage(self.request).addStatusMessage(u"Correggi gli errori evidenziati", type = 'error')
            return self.context.restrictedTraverse('@@add-follower-page')()

        email = ''
        fullname = ''

        self.context.plone_log("Following: %s" % str(self.request.form))

        # if container:
        #     email = data['email'].strip()
        #
        #     brains = self.context.portal_catalog.unrestrictedSearchResults(portal_type = 'Follower')
        #
        #     already_subscribed = []
        #     for x in brains:
        #         x_obj = self.context.unrestrictedTraverse(x.getPath())
        #         if x_obj.getEmail().strip().lower() == email.lower():
        #             already_subscribed.append(x_obj)
        #
        #     ctf = self.context if data['typology'] == 'comments' else self.clab_utils.getContentToFollow(self.context)
        #
        #     if already_subscribed:
        #         subscriber = already_subscribed[0]
        #         ctfs = [x for x in subscriber.getFollowing()]
        #
        #         if self.context.getId() == 'felicita-sostenibile':
        #             subscriber.setAddress(data.get('address'))
        #             subscriber.setCity(data.get('city'))
        #             subscriber.setZip_code(data.get('zip_code'))
        #             subscriber.setNotes(data.get('notes'))
        #
        #         if ctf:
        #             uid = ctf.UID()
        #             if uid not in ctfs:
        #                 ctfs.append(uid)
        #             else:
        #                 IStatusMessage(self.request).addStatusMessage(al_error, type = 'info')
        #                 redirect = '%s/@@already-following' % self.context.absolute_url()
        #                 return response.redirect(redirect)
        #     else:
        #         fullname = '%s %s' % (data['firstname'], data['lastname'])
        #         raw_obj_id = self.context.plone_utils.normalizeString(fullname)
        #         obj_id = raw_obj_id
        #         if obj_id in [r[0] for r in container.items()]:
        #             counter = 0
        #             while obj_id in [r[0] for r in container.items()]:
        #                 counter += 1
        #                 obj_id = '%s-%s' % (raw_obj_id, counter)
        #
        #         ctfs = []
        #         if ctf:
        #             ctfs.append(ctf.UID())
        #
        #         subscriber = _createObjectByType('Follower', container, id = obj_id)
        #         subscriber.setTitle(data['lastname'].strip())
        #         subscriber.setFirstname(data['firstname'].strip())
        #         subscriber.setEmail(email)
        #         subscriber.setProvince(data['province'])
        #         subscriber.setProvince_details(data.get('province_details'))
        #
        #         if self.context.getId() == 'felicita-sostenibile':
        #             subscriber.setAddress(data.get('address'))
        #             subscriber.setCity(data.get('city'))
        #             subscriber.setZip_code(data.get('zip_code'))
        #             subscriber.setNotes(data.get('notes'))
        #
        #         try:
        #             subscriber.getField('code').set(subscriber, self.generateRandomCode())
        #         except:
        #             pass
        #
        #     subscriber.getField('following').set(subscriber, tuple(ctfs))
        #     subscriber.reindexObject()

        # set cookie
        data_string = '%s||%s||%s||%s||%s' % (data['lastname'].strip(), data['firstname'].strip(), email, data['province'], data.get('province_details', ''))
        new_cookie = base64.b64encode(data_string)
        expires = (datetime.datetime.now() + datetime.timedelta(60)).strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        response.setCookie('clabfollow', '%s' % new_cookie, path = '/', expires = '%s' % expires)

        # newSecurityManager(None, user)
        IStatusMessage(self.request).addStatusMessage(ok, type = 'info')
        if fullname:
            redirect = '%s/@@follow-thanks?fullname=%s' % (self.context.absolute_url(), fullname)
        else:
            redirect = '%s/@@follow-thanks' % self.context.absolute_url()