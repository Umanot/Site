# -*- coding: utf-8 -*-
import copy
import json
from decimal import Decimal
from xml.etree.ElementTree import fromstring

import oursql

import requests
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from umanot.site.config import SQL_HOST_TEST, SQL_USER_TEST, SQL_PASS_TEST, SQL_DB_TEST, SQL_HOST, SQL_USER, SQL_PASS, SQL_DB
from zope.annotation import IAnnotations
from zope.component.hooks import getSite
from zope.interface import implements, Interface


class IUmanotUtils(Interface):
    """sol utility"""


class UmanotUtils(object):
    implements(IUmanotUtils)

    def get_posts_by_portfolio(self, portfolio):
        url = "http://5.189.150.24/umanot_ws/WebPost.asmx/BindGrid"

        params = {'Portfolio': portfolio}

        response = requests.get(url, params = params)

        data = fromstring(response.text)
        json_data = json.loads(data.text)

        results = []

        base_path = 'http://5.189.150.24/umanot/UmanotImage/'

        for item in json_data:
            has_image = bool(item['destimage'])
            info = dict(
                symbol = item['Symbol'],
                share = item['Share'],
                mode = item['Mode'],
                date = DateTime(item['Date']),
                has_image = has_image,
                image = base_path + '/' + item['destimage'] if has_image else '',
                post = item['Post']
            )

            results.append(info)

        results.sort(lambda x, y: cmp(y['date'], x['date']))

        return results

    def money_from_float(self, float_value, show_currency=True, show_decimals=True, show_plus=False):
        if not float_value:
            results = '0,00' if show_decimals else '0'

            if show_currency:
                results += ' €'

            return results

        money = '%.2f' % float_value
        money = money.replace('.', ',')

        money = money[:-6] + '.' + money[-6:] if abs(float_value) >= 1000 else money

        if not show_decimals:
            money = money.split(',')[0]

        if show_currency:
            money += ' €'

        if show_plus and float_value > 0:
            money = '+%s' % money

        return money

    def float_from_money(self, money, decimal=False, null_is_zero=False):
        if null_is_zero and not money:
            return 0

        WHITELIST = '0123456789,.'
        money = ''.join([x for x in money if x in WHITELIST])

        if '.' in money and ',' in money:
            if money.find('.') < money.find(','):
                money = money.replace('.', '')
            else:
                money = money.replace(',', '')

        if ',' in money:
            money = money.replace(',', '.')

        float_value = float(money)

        if decimal:
            return Decimal(str(float_value)).quantize(Decimal('.01'))
        else:
            return float_value

    def get_sql_connection(self, url, context=None):
        if 'localhost' in url or 'mediatria.com' in url:
            connection = oursql.connect(SQL_HOST_TEST, SQL_USER_TEST, SQL_PASS_TEST, db = SQL_DB_TEST)
            if context:
                context.plone_log("Test DB connection")
        else:
            connection = oursql.connect(SQL_HOST, SQL_USER, SQL_PASS, db = SQL_DB)

        return connection

    def prepare_data_for_query(self, data):
        if isinstance(data, basestring):
            return self.quote_param(data)

        if isinstance(data, dict):
            for k, v in data.iteritems():
                data[k] = self.quote_param(v)

        if isinstance(data, list):
            data = [self.quote_param(x) for x in data]

        return data

    def quote_param(self, v):
        if isinstance(v, basestring):
            v = v.replace("'", "''")
            return v

        return v

    def is_stage(self, request):
        if 'localhost' in request.get('URL') or 'mediatria.com' in request.get('URL'):
            return True

    def get_area_from_context(self, context):
        if context.portal_type in ["Article", "Placeholder"]:
            parent = context.aq_parent
            if parent.portal_type == "Folder":
                return parent
        elif context.portal_type == 'Folder':
            return context

    def setLocalAd(self, context, data):
        KEY = 'umanot.ad'
        context = context.aq_inner
        annotations = IAnnotations(context)

        if not data and annotations.get(KEY):
            del (annotations[KEY])
            context.plone_log("Ad removed")
            return

        results = copy.copy(data)

        annotations[KEY] = results

    def getLocalAd(self, context):
        KEY = 'umanot.ad'
        context = context.aq_inner

        try:
            annotations = IAnnotations(context)
        except TypeError:
            return

        results = annotations.get(KEY)

        return results

    def getAdImages(self):
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')

        images = catalog(
            portal_type = 'Image',
            path = '/umanot/it/risorse/immagini/bnr',
            sort_on = 'getObjPositionInParent',
            Language = 'all'
        )

        return images

    # def getSector(self, context):
    #     parent = context.aq_inner
    #     try:
    #         while parent.portal_type != 'Sector':
    #             parent = parent.aq_parent
    #         return parent
    #     except:
    #         return None

    def notifyFollowers(self, context, typology='area_tematica', action='new'):
        # nel caso di commenti il contenuto da notificare è il context, non devo risalire a nulla
        if typology == 'comments':
            parent = context

            try:
                while True:
                    if hasattr('addComment') or parent.portal_type == 'Discussion Item':
                        parent = parent.aq_parent
                    else:
                        break
            except:
                pass

            followed_obj = parent
        elif typology == 'area_tematica':
            if context.portal_type in ["Article", "Placeholder"]:
                followed_obj = self.get_area_from_context(context)
            else:
                followed_obj = context
        else:
            # questo caso non è detto che sia sensato
            followed_obj = context

        uid = followed_obj.UID()

        sqldata = {
            'uid': uid,
            'typology': typology,
        }

        request = context.REQUEST

        sqldata = self.prepare_data_for_query(sqldata)
        connection = self.get_sql_connection(request.get('URL'))
        cursor = connection.cursor()

        if typology == 'area_tematica' and uid != '943e809ec82e4b0eb9ea803314a1fefd':  # TODO: sistemare, in pratica quando si fa il follow d osserva umanot esce area uid = NULL ma la tipologia dovrebbe essere area_tematica. Fixare o il follow (che imposti anche l'area UID) o qui in qualche modo
            query = """SELECT Email FROM Followers WHERE AreaUID='%(uid)s' AND Typology='%(typology)s'""" % sqldata
        else:
            query = """SELECT Email FROM Followers WHERE ContentUID='%(uid)s' AND Typology='%(typology)s'""" % sqldata

        cursor.execute(query)

        records = cursor.fetchall()

        recipient = [x[0] for x in records]

        if not recipient:
            context.plone_log('Notification error: no recipient')
            return

        recipient = list(set(recipient))

        # recipient = ['francesco@mediatria.com']

        sender = 'staff@umanot.com'

        if typology == 'area_tematica':
            if action == 'update':
                if uid == '943e809ec82e4b0eb9ea803314a1fefd':
                    subject = "Update Osserva Umanot in azione - %s" % context.toLocalizedTime(DateTime(), long_format = False)
                    body = '<p>Abbiamo pubblicato un nuovo aggiornamento dei risultati di Umanot.</p>'
                    body += '<p><a href="http://www.umanot.com/it/servizi/osserva-umanot-in-azione">ACCEDI SUBITO ALLA PAGINA</a></p>'
                else:
                    subject = "[Umanot update] %s" % self.safeencode(followed_obj.Title())
                    body = '<p>È stato modificato il contenuto: <a href="%s">%s</a></p>' % (context.absolute_url(), self.safeencode(context.Title()))
                body += "<p>Grazie per tuoi commenti e contributi!</p><p>Lo staff di Umanot</p>"
            else:
                subject = "[Umanot update] %s" % self.safeencode(followed_obj.Title())
                body = '<p>È stato aggiunto il contenuto: <a href="%s">%s</a></p>' % (context.absolute_url(), self.safeencode(context.Title()))
                body += "<p>Grazie per tuoi commenti e contributi!</p><p>Lo staff di Umanot</p>"
        elif typology == 'comments':
            subject = "[Umanot] %s" % self.safeencode(followed_obj.Title())
            body = '<p>È stato inserito un nuovo commento: <a href="%s">%s</a></p>' % (context.absolute_url(), self.safeencode(context.Title()))
            body += "<p>Grazie per tuoi commenti e contributi!</p><p>Lo staff di Umanot</p>"
        else:
            context.plone_log('Notification error: wrong typology')
            return

        for email in recipient:
            info = dict(
                receiver = email,
                subject = self.safedecode(subject),
                message = self.safedecode(body),
                sender = sender
            )

            context.plone_log(u'Sending mail for %s to: %s - %s - %s' % (self.safedecode(followed_obj.Title()), self.safedecode(email), self.safedecode(subject), self.safedecode(body)))

            if '.mediatria.com' in context.REQUEST.get('URL') or 'localhost' in context.REQUEST.get('URL'):
                self.notifySingleUser(info)
                break
            else:
                self.notifySingleUser(info)

        return True

    def notifySingleUser(self, info):
        """Send message to one or more user.
           The info parameter must contain at least:
           - receiver email address
           - subject
           Optionally we can have:
           - message
        """
        site = getSite()
        plone_utils = getToolByName(site, 'plone_utils')
        mailHost = plone_utils.getMailHost()

        # required info
        if not info.get('subject') or not info.get('receiver'):
            return

        # SENDER/RECEIVER ADDRESSES
        send_from_address = info['sender'] if info.get('sender') else 'no-reply@umanot.com'
        send_to_address = info.get('receiver')

        custom_data = dict(
            logo_url = 'http://www.umanot.com/++resource++umanot.site.images/logo_pos.svg',
            portal_title = "Umanot"
        )
        # TYPE
        subtype = 'text/html'

        # SUBJECT AND BODY
        subject = info['subject']

        mail_head = u"""
            <!DOCTYPE html PUBLIC “-//W3C//DTD XHTML 1.0 Transitional//EN” “http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd”>
              <html>
              <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <title>%s</title>
              </head>""" % info['subject']

        mail_body = u"""<body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0" style="background-color: #fff; text-align: center; font-family: Arial, sans-serif; font-size: 12px; margin: 0; padding: 0; color: #333333;">

    <style>
        .tableContent,
        .tableContent p,
        .tableContent ul {font-size: 13px;}
        @media only screen and (min-width: 1024px) {
            .tableContent {
                width: 80%%!important;
            }
        }

        @media only screen and (max-width: 538px) {
            .tdContent {
                padding: 20px 15px!important;
            }
        }
    </style>

    <table cellpadding="0" cellspacing="0" style="width: 100%%; background-color: #ffffff; border-bottom: 4px solid #D1061F;border-collapse: collapse; font-family: Arial, sans-serif;">
        <tr>
            <td style="padding: 0; vertical-align: top;" valign="top">

                <table cellpadding="0" cellspacing="10">
                    <tr>
                        <td></td>
                    </tr>
                </table>
                <table cellpadding="0" cellspacing="0" class="tableContent" align="center" width="90%%" style="width: 90%%; margin: 0 auto; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 0; vertical-align: middle;" align="left" valign="top">
                            <img width="148" height="30" src="%(logo_url)s" title="%(portal_title)s" alt="%(portal_title)s" border="0">
                        </td>
                    </tr>
                </table>
                <table cellpadding="0" cellspacing="10">
                    <tr>
                        <td></td>
                    </tr>
                </table>

            </td>
        </tr>
    </table>

    <table cellpadding="0" cellspacing="10">
        <tr>
            <td></td>
        </tr>
    </table>


    <table cellpadding="0" cellspacing="0" class="tableContent" width="90%%" align="center" style="background-color: #ffffff; width: 90%%; text-align: left; margin: 0 auto;">
        <tr>
            <td class="tdContent" align="left">""" % custom_data

        # MESSAGE
        mail_body += self.safedecode(info.get('message', ''))

        # FOOTER
        mail_footer = u"""
              </td>
        </tr>
    </table>

    <table cellpadding="0" cellspacing="10">
        <tr>
            <td></td>
        </tr>
    </table>


    <table cellpadding="0" cellspacing="10">
        <tr>
            <td></td>
        </tr>
    </table>


</body>
</html>"""

        message = '%s%s%s' % (mail_head, mail_body, mail_footer)

        subject = self.safeencode(subject)
        message = self.safeencode(message)

        mailHost.send(message, mto = send_to_address, mfrom = send_from_address, subject = subject, msg_type = subtype, charset = 'utf-8')

        return True

    def sendmail(self, mailfrom, mailto, mailBody, subject=None, debug=False):
        """"""
        site = getSite()
        subtype = 'text/html'
        mail_host = getattr(site, 'MailHost', None)

        subject = self.safeencode(subject)
        mailBody = self.safeencode(mailBody)

        if debug:
            site.plone_log('Sending mail to: %s - %s - %s' % (mailto, subject, mailBody))

        # mail_host.send(mailBody, mto=mailto, mfrom=mailfrom, subject=subject, msg_type=subtype)
        mail_host.send(mailBody, mto = mailto, mfrom = mailfrom, subject = subject, msg_type = subtype, charset = 'utf-8')

    def safeencode(self, v):
        if isinstance(v, unicode):
            return v.encode('utf-8')
        return v

    def safedecode(self, v):
        if isinstance(v, str):
            return v.decode('utf-8')
        return v
