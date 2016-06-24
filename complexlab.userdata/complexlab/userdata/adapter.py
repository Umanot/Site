from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType


class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """
    """

    def get_company(self):
        return unicode(self.context.getProperty('company', ''), 'utf-8')

    def set_company(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'company': value})

    company = property(get_company, set_company)

    def get_role(self):
        return unicode(self.context.getProperty('role', ''), 'utf-8')

    def set_role(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'role': value})

    role = property(get_role, set_role)

    # def get_professional_profile(self):
    #         return self.context.getProperty('professional_profile', '')
    #     def set_professional_profile(self, value):
    #         if not value: value = ''
    #         return self.context.setMemberProperties({'professional_profile': value})
    #     professional_profile = property(get_professional_profile, set_professional_profile)

    def get_cv(self):
        #=======================================================================
        # container = self.context.restrictedTraverse('/complexlab/cv')
        # mid = self.context.id
        # cv = None
        #=======================================================================
        mid = self.context.id
        mtool = getToolByName(self.context, 'portal_membership')
        container = mtool.getHomeFolder(mid)

        if not container:
            return

        cvid = 'cv'
        if cvid in container.keys():
            cv = getattr(container, cvid)
            if cv.size() > 0:
                return cv


    def set_cv(self, value):
        if value:
            #===================================================================
            # container = self.context.restrictedTraverse('/complexlab/cv')
            # mid = self.context.id
            # if mid not in container.keys():
            #===================================================================
            mid = self.context.id
            mtool = getToolByName(self.context, 'portal_membership')
            container = mtool.getHomeFolder(mid)

            if not container:
                return

            cvid = 'cv'
            if cvid not in container.keys():
                _createObjectByType("File", container, id = cvid, title = 'CV di %s' % self.context.getProperty('fullname'))

            cv = getattr(container, cvid)
            cv.setFile(value.read())
            cv.setFilename(value.filename)
            cv.reindexObject()
            #context.portal_membership.changeMemberCV(value, context.id)

    cv = property(get_cv, set_cv)

    def get_cvdelete(self):
        pass

    def set_cvdelete(self, value):
        if value:
            #===================================================================
            # container = self.context.restrictedTraverse('/complexlab/cv')
            # mid = self.context.id
            # cv = None
            #===================================================================
            mid = self.context.id
            mtool = getToolByName(self.context, 'portal_membership')
            container = mtool.getHomeFolder(mid)
            cvid = 'cv'
            if cvid in container.keys():
                cv = getattr(container, cvid)
                cv.setFile(None)
                cv.setFilename('')
                cv.reindexObject()

    cvdelete = property(get_cvdelete, set_cvdelete)

    #     def get_city(self):
    #         return self.context.getProperty('city', '')
    #     def set_city(self, value):
    #         if not value: value = ''
    #         return self.context.setMemberProperties({'city': value})
    #     city = property(get_city, set_city)
    #
    #     def get_website(self):
    #         return self.context.getProperty('website', '')
    #     def set_website(self, value):
    #         if not value: value = ''
    #         return self.context.setMemberProperties({'website': value})
    #     website = property(get_website, set_website)

    def get_phone(self):
        return self.context.getProperty('phone', '')

    def set_phone(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'phone': value})

    phone = property(get_phone, set_phone)

    def get_mobile(self):
        return self.context.getProperty('mobile', '')

    def set_mobile(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'mobile': value})

    mobile = property(get_mobile, set_mobile)

    def get_skype(self):
        return self.context.getProperty('skype', '')

    def set_skype(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'skype': value})

    skype = property(get_skype, set_skype)

    def get_linkedin(self):
        return self.context.getProperty('linkedin', '')

    def set_linkedin(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'linkedin': value})

    linkedin = property(get_linkedin, set_linkedin)

    def get_twitter(self):
        return self.context.getProperty('twitter', '')

    def set_twitter(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'twitter': value})

    twitter = property(get_twitter, set_twitter)

    def get_facebook(self):
        return self.context.getProperty('facebook', '')

    def set_facebook(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'facebook': value})

    facebook = property(get_facebook, set_facebook)
    
    def get_partita_iva(self):
        return self.context.getProperty('partita_iva', '')

    def set_partita_iva(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'partita_iva': value})

    partita_iva = property(get_partita_iva, set_partita_iva)
    
    def get_province(self):
        return self.context.getProperty('province', '')

    def set_province(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'province': value})

    province = property(get_province, set_province)
    
    def get_ente(self):
        return self.context.getProperty('ente', '')

    def set_ente(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'ente': value})

    ente = property(get_ente, set_ente)

    def get_competenze(self):
        return self.context.getProperty('competenze', [])

    def set_competenze(self, value):
        if not value: value = []
        return self.context.setMemberProperties({'competenze': value})

    competenze = property(get_competenze, set_competenze)

    def get_email_confirm(self):
        return self.context.getProperty('email_confirm', '')

    def set_email_confirm(self, value):
        if not value: value = ''
        return self.context.setMemberProperties({'email_confirm': value})

    email_confirm = property(get_email_confirm, set_email_confirm)

    def get_tos(self):
       return self.context.getProperty('tos', '')
    def set_tos(self, value):
       if not value: value = ''
       return self.context.setMemberProperties({'tos': value})
    tos = property(get_tos, set_tos)

    #===========================================================================
    # def get_utentec6(self):
    #    return self.context.getProperty('utentec6', '')
    # def set_utentec6(self, value):
    #    if not value: value = ''
    #    return self.context.setMemberProperties({'utentec6': value})
    # utentec6 = property(get_utentec6, set_utentec6)
    #===========================================================================
