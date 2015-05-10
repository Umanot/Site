# -*- coding: utf-8 -*-
import base64
from random import choice

from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation import validation as validationService
from Products.CMFPlone.utils import _createObjectByType
import datetime
import oursql

class IAddFollower(Interface):
    """
    AddFollower view interface
    """


class AddFollower(BrowserView):
    """
    AddFollower browser view
    """
    implements(IAddFollower)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        request = self.request
        response = request.RESPONSE
        
        conn = oursql.connect(host='localhost', user='root', passwd='112d24e2', db='ComplexLab')

        errors = dict()
        data = dict()

        is_en = 'scientific-spirituality' in self.context.getPhysicalPath()

        if not is_en:
            fn_error = "Inserisci il tuo nome"
            ln_error = "Inserisci il tuo cognome"
            pr_error = "Inserisci la tua provincia di residenza"
            em_error = "Inserisci il tuo indirizzo email"
            nv_error = "Indirizzo email non valido"
            sm_error = u"Correggi gli errori"
            al_error = u"Questo indirizzo e-mail è già registrato per questo progetto"
            ok = u"La tua richiesta è stata inoltrata correttamente"
        else:
            fn_error = "Name is required"
            ln_error = "Lastname is required"
            pr_error = "Country is required"
            em_error = "Email il required"
            nv_error = "Email address not valid"
            sm_error = "There are some errors"
            al_error = "Email address already present"
            ok = u"Your request has been succesfully processed"

        for k, v in request.form.items():
            if k == 'firstname' and not v:
                errors['firstname'] = fn_error
            if k == 'lastname' and not v:
                errors['lastname'] = ln_error
            if k == 'province' and v == '--':
                errors['province'] = pr_error
            if k == 'email':
                validator = validationService.validatorFor('isEmail')
                if not v:
                    errors['email'] = em_error
                elif validator(v) != 1:
                    errors['email'] = nv_error

            data[k] = v

        if errors:
            self.request.form['follow-errors'] = errors
            for data_k, data_v in data.items():
                self.request.form[data_k] = data_v

            IStatusMessage(self.request).addStatusMessage(sm_error, type = 'error')
            return self.context.restrictedTraverse('@@follow-form')()

        container = self.clab_utils.getFollowersFolder(self.context)
        email = ''
        fullname = ''

        self.context.plone_log("Following: %s" % str(self.request.form))

        if container:
            email = data['email'].strip()

            brains = self.context.portal_catalog.unrestrictedSearchResults(portal_type = 'Follower')

            already_subscribed = []
            for x in brains:
                x_obj = self.context.unrestrictedTraverse(x.getPath())
                if x_obj.getEmail().strip().lower() == email.lower():
                    already_subscribed.append(x_obj)

            ctf = self.context if data['typology'] == 'comments' else self.clab_utils.getContentToFollow(self.context)

            if already_subscribed:
                subscriber = already_subscribed[0]
                ctfs = [x for x in subscriber.getFollowing()]

                if self.context.getId() == 'felicita-sostenibile':
                    subscriber.setAddress(data.get('address'))
                    subscriber.setCity(data.get('city'))
                    subscriber.setZip_code(data.get('zip_code'))
                    subscriber.setNotes(data.get('notes'))

                if ctf:
                    uid = ctf.UID()
                    if uid not in ctfs:
                        ctfs.append(uid)
                    else:
                        IStatusMessage(self.request).addStatusMessage(al_error, type = 'info')
                        redirect = '%s/@@already-following' % self.context.absolute_url()
                        return response.redirect(redirect)
            else:
                fullname = '%s %s' % (data['firstname'], data['lastname'])
                raw_obj_id = self.context.plone_utils.normalizeString(fullname)
                obj_id = raw_obj_id
                if obj_id in [r[0] for r in container.items()]:
                    counter = 0
                    while obj_id in [r[0] for r in container.items()]:
                        counter += 1
                        obj_id = '%s-%s' % (raw_obj_id, counter)

                ctfs = []
                if ctf:
                    ctfs.append(ctf.UID())

                subscriber = _createObjectByType('Follower', container, id = obj_id)
                subscriber.setTitle(data['lastname'].strip())
                subscriber.setFirstname(data['firstname'].strip())
                subscriber.setEmail(email)
                subscriber.setProvince(data['province'])
                subscriber.setProvince_details(data.get('province_details'))

                if self.context.getId() == 'felicita-sostenibile':
                    subscriber.setAddress(data.get('address'))
                    subscriber.setCity(data.get('city'))
                    subscriber.setZip_code(data.get('zip_code'))
                    subscriber.setNotes(data.get('notes'))

                try:
                    subscriber.getField('code').set(subscriber, self.generateRandomCode())
                except:
                    pass

            subscriber.getField('following').set(subscriber, tuple(ctfs))
            subscriber.reindexObject()

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



        return response.redirect(redirect)

    def generateRandomCode(self):
        code = ''
        candidates = '123456789abcdefghmnpqrstuvwxyzABCDEFGHMNPQRSTUVWXYZ'
        for x in range(6):
            code += choice(candidates)
        return code


