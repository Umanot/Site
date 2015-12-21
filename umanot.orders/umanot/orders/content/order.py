# -*- coding: utf-8 -*-
"""Definition of the Order content type
"""
import copy
from archetypes.referencebrowserwidget import ReferenceBrowserWidget

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocument
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
from umanot.orders.config import PROJECTNAME
from umanot.orders.interfaces.order import IOrder


OrderSchema = document.ATDocumentSchema.copy() + atapi.Schema((
    atapi.StringField(
        name = 'number',
        required = True,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"Numero",
        )
    ),
    # atapi.StringField(
    #     name = 'discount_code',
    #     required = 0,
    #     searchable = 0,
    #     storage = atapi.AnnotationStorage(),
    #     widget = atapi.StringWidget(
    #         label = 'Codice sconto',
    #     ),
    # ),
    atapi.TextField(
        name = 'customer',
        required = 0,
        searchable = 0,
        storage = atapi.AnnotationStorage(),
        default_output_type = 'text/html',
        widget = atapi.TextAreaWidget(
            label = _(u"Anagrafica acquirente"),
            rows = 4
        ),
    ),
    atapi.StringField(
        name = 'status',
        required = 0,
        searchable = 0,
        default = 'annullato',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = 'Stato',
        ),
    ),
    atapi.StringField(
        name = 'email',
        required = True,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"User E-mail",
        )
    ),
    atapi.StringField(
        name = 'username',
        required = True,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = u"User ID",
        )
    ),
    atapi.IntegerField(
        name = "vat",
        required = True,
        default = 22,
        storage = atapi.AnnotationStorage(),
        widget = atapi.IntegerWidget(
            label = u"IVA",
        )
    ),
    atapi.FloatField(
        name = 'net',
        required = True,
        storage = atapi.AnnotationStorage(),
        widget = atapi.DecimalWidget(
            label = u"Importo (IVA esclusa)",
        )
    ),
    atapi.ReferenceField(
        name = 'product',
        multiValued = False,
        relationship = 'orders',
        widget = ReferenceBrowserWidget(
            label = u"Prodotto",
            startup_directory = '',
        ),
    ),
    atapi.IntegerField(
        name = "quantity",
        required = True,
        default = 1,
        storage = atapi.AnnotationStorage(),
        widget = atapi.IntegerWidget(
            label = u"Quantità"
        ),
    ),
    atapi.ReferenceField(
        name = 'discount_code',
        multiValued = False,
        relationship = 'discount_codes',
        widget = ReferenceBrowserWidget(
            label = u"Codice sconto",
            startup_directory = '',
        ),
    ),
    # atapi.FloatField(
    # name = 'gross',
    #     required = True,
    #     storage = atapi.AnnotationStorage(),
    #     widget = atapi.DecimalWidget(
    #         label = u"Importo (IVA inclusa)",
    #     )
    # ),
))

OrderSchema['title'].storage = atapi.AnnotationStorage()
OrderSchema['title'].required = 1
OrderSchema['title'].searchable = 0
OrderSchema['description'].storage = atapi.AnnotationStorage()
OrderSchema['description'].required = 0
OrderSchema['description'].searchable = 0
OrderSchema['description'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
OrderSchema['text'].required = 0
OrderSchema['text'].searchable = 0
#OrderSchema['text'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
OrderSchema['customer'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
OrderSchema['discount_code'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
OrderSchema['status'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

schemata.finalizeATCTSchema(OrderSchema)


class Order(ATDocument):
    """The Order item"""

    implements(IOrder)

    portal_type = "Order"
    schema = OrderSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def getInfo(self):
        net = self.getNet()
        vat = self.getVat() / 100.
        gross = net * float(1 + vat)

        status_map = {
            'pending': 'Da processare',
            'annullato': 'Annullato',
            'confermato': 'Confermato'
        }

        info = dict(
            title = self.Title(),
            description = self.Description(),
            URL = self.absolute_url(),
            details = self.getText(),
            net = net,
            vat = vat,
            readable_vat = self.getVat(),
            vat_amount = net * vat,
            gross = gross,
            number = self.getNumber(),
            readable_created = self.created().strftime('%d/%m/%Y'),
            status = self.getStatus(),
            readable_status = status_map.get(self.getStatus()),
        )

        return info

    def processAction(self, action=''):
        if not action:
            return 'Error: no action'

        if self.getStatus() == action:
            return

        if action == 'confermato':
            self.setStatus('confermato')

        if action == 'annullato':
            self.setStatus('annullato')

        self.reindexObject()

    def saveData(self, data, KEY, base={}):
        annotations = IAnnotations(self)
        results = annotations.get(KEY)

        if not results:
            results = copy.copy(base)

        if isinstance(base, dict):
            for k, v in data.items():
                results[k] = v
        elif isinstance(base, list):
            results = data[:]

        annotations[KEY] = results

    def readData(self, KEY, base={}):
        annotations = IAnnotations(self)

        base = copy.copy(base)
        results = annotations.get(KEY, base)

        return results

    def printAnnotations(self):
        annotations = IAnnotations(self)

        for k, v in annotations.items():
            print '%s    >    %s' % (k, str(v))
            print "\n\n"

    def notifyCustomer(self):
        context = self
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()

        plone_utils = getToolByName(context, 'plone_utils')

        host = context.MailHost
        encoding = portal.getProperty('email_charset')

        send_from_address = portal.getProperty('email_from_address', 'somebody@somebody.org')

        send_to_address = ['saviano@mediatria.com']
        # send_to_address = ['saviano@mediatria.com']
        subtype = 'html'

        mail_head = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
        <html lang="it">
        <head>
        <meta http-equiv="Content-Type" content="text/html" charset="UTF-8">
        <style>
            body, html {margin:0; padding:0px; font-size:100%%;}
            h2 {color:#333; font-weight:bold; font-size:120%%;}
            h3 {color:#C9B973; font-weight:bold; font-size:110%%;}
            table {border-collapse: collapse; border:0px; margin-top:20px;}
            td, th {border-bottom:1px solid #EEEEEE; padding:5px 8px;}
            th {background-color:#F8F8F8;}
            .lordo {background-color:#eee;}
            .total {background-color:#dedede;}
            #header {border-top: 20px solid #F8F8F8; margin-bottom:30px;}
            #header img {margin:-10px 0 0 30px;}
            #content {margin:0 30px 60px;}
        </style>
        <title>Umanot</title>
        </head>
        """

        mail_body = """<body>
        <div id="header">
                 <img width="170" height="158" title="" alt="" src="http://complexlab.it/logo.png">
           </div><div id="content">
        """
        warehouseman_intro = '<h2>Hai ricevuto un nuovo ordine su www.complexlab.it</h2><br />'
        customer_intro = '<h2>Hai effettuato un ordine su www.complexlab.it</h2><br />'

        message = """
        """

        message += """
          </tbody>
        </table>
        """

        warehouseman_link = """<p>Trovi i dettagli di questo ordine all'indirizzo: <a href="%s">%s</a></p>""" % (self.absolute_url(), self.absolute_url())

        footer = '</div></body></html>'

        warehouseman_message = mail_head + mail_body + warehouseman_intro + '' + message + '' + warehouseman_link + '' + footer
        customer_message = mail_head + mail_body + customer_intro + '' + message + '' + footer

        # email subject
        subject = 'Umanot [%s]' % self.getId()
        subject = subject.strip()

        try:
            for s_add in send_to_address:
                host.secureSend(warehouseman_message, s_add, send_from_address, subject = subject, subtype = subtype, charset = encoding, debug = False, From = send_from_address)
            host.secureSend(customer_message, self.getCustomer_email(), send_from_address, subject = subject, subtype = subtype, charset = encoding, debug = False, From = send_from_address)
        except ConflictError:
            raise
        except:  # TODO Too many things could possibly go wrong. So we catch all.
            exception = plone_utils.exceptionString()
            message = _(u'Unable to send mail: ${exception}',
                        mapping = {u'exception': exception})
            plone_utils.addPortalMessage(message, 'error')
            return context.REQUEST.RESPONSE.redirect('%s' % context.absolute_url())


atapi.registerType(Order, PROJECTNAME)