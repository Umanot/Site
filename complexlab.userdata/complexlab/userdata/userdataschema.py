# -*- coding: utf-8 -*-
from zope.interface import implements
from zope import schema

from complexlab.userdata import _

from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.userdataschema import IUserDataSchema
from Products.CMFDefault.formlib.schema import FileUpload


# def validateAccept(value):
# if not value == True:
#         return False
#     return True

class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IEnhancedUserDataSchema


class IEnhancedUserDataSchema(IUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """

    company = schema.TextLine(
        title = _(u'label_company', default = u'Azienda'),
        description = _(u'help_company',
                        default = u""),
        required = False,
    )
    role = schema.TextLine(
        title = _(u'label_role', default = u'Ruolo'),
        description = _(u'help_role',
                        default = u""),
        required = False,
    )
    cv = FileUpload(title = _(u'label_cv', default = u"Curriculum Vitae"),
                    description = _(u'help_cv',
                                    default = u''),
                    required = False)
    cvdelete = schema.Bool(
        title = _(u'label_delete_cv', default = 'Cancella Curriculum Vitae'),
        description = u'',
        required = False)
    phone = schema.TextLine(
        title = _(u'label_phone', default = u"Telefono"),
        description = _(u'help_phone',
                        default = u""),
        required = False,
    )
    mobile = schema.TextLine(
        title = _(u'label_mobile', default = u"Cellulare"),
        description = _(u'help_mobile',
                        default = u""),
        required = False,
    )
    skype = schema.TextLine(
        title = _(u'label_skype', default = u"Skype"),
        description = _(u'help_skype',
                        default = u""),
        required = False,
    )
    linkedin = schema.TextLine(
        title = _(u'label_linkedin', default = u"LinkedIn"),
        description = _(u'help_linkedin',
                        default = u""),
        required = False,
    )
    twitter = schema.TextLine(
        title = _(u'label_twitter', default = u"Twitter"),
        description = _(u'help_twitter',
                        default = u""),
        required = False,
    )
    facebook = schema.TextLine(
        title = _(u'label_facebook', default = u"Facebook"),
        description = _(u'help_facebook',
                        default = u""),
        required = False,
    )
    partita_iva = schema.TextLine(
        title = _(u'label_partita_iva', default = u"Partita IVA"),
        description = _(u'help_partita_iva',
                        default = u""),
        required = False,
    )
    province = schema.TextLine(
        title = _(u'label_province', default = u"Provincia"),
        description = _(u'help_province',
                        default = u""),
        required = False,
    )
    ente = schema.TextLine(
        title = _(u'label_ente', default = u"Convenzione"),
        description = _(u'help_ente',
                        default = u""),
        required = False,
    )
    email_confirm = schema.TextLine(
        title = _(u'email_confirm', default = u"Conferma l'indirizzo di posta elettronica"),
        description = _(u'email_confirm',
                        default = u""),
        required = True,
    )
    competenze = schema.List(
        title = _(u'label_competenze', default = u"Competenze"),
        description = _(u'help_competenze',
                        default = u"Inserisci massimo 5 competenze, una per riga"),
        required = False,
        value_type=schema.TextLine(required=False),
    )
    tos = schema.Bool(
        title = u"Con la registrazione a ComplexLab accetti integralmente i seguenti documenti: Informativa sulla Privacy, Cookie Policy, Disclaimer, Condizioni generali di Uso e di Vendita, Guida ai comportamenti corretti (consultabili ai link in fondo a questa pagina)",
        required = True
    )
    #===========================================================================
    # utentec6 = schema.Bool(
    #    title=_(u'label_c6', default=u"Utente C6"),
    #    description=_(u'help_c6',
    #                  default=u""),
    #    required=False,
    #    )
    #===========================================================================

