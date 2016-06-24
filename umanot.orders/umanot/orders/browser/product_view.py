# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from umanot.site.browser.umanot_utils import IUmanotUtils
from plone.memoize.instance import memoize
from zope.component import getUtility
from zope.interface import implements, Interface

from Products.Five import BrowserView


class IProductView(Interface):
    """
    Order view interface
    """


class ProductView(BrowserView):
    """
    Order browser view
    """
    implements(IProductView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.limit = 2
        self.min_date = request.get('min_date', '')
        self.last_uid = request.get('last_uid')
        self.umanot_utils = getUtility(IUmanotUtils)

    @property
    def title(self):
        return self.context.Title()

    @property
    def can_manage(self):
        mtool = getToolByName(self.context, 'portal_membership')

        if mtool.isAnonymousUser():
            return

        auth = mtool.getAuthenticatedMember()

        return auth.has_role('Manager')

    @property
    def is_anonymous(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.isAnonymousUser()

    @property
    @memoize
    def info(self):
        info = self.context.getInfo()

        info['text'] = self.get_data(info)['text']

        return info

    @property
    def discount_info(self):
        if not self.request.get('code'):
            return

        code = self.request['code']

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type = "DiscountCode",
        )

        objs = [self.context.unrestrictedTraverse(x.getPath()) for x in brains]

        codes = [x for x in objs if x.getCode().lower().strip() == code.lower().strip()]

        for code in codes:
            if self.context not in code.getProducts():
                continue

            return code.get_prices_for_product(self.context)

    def renderMoney(self, value):
        return self.umanot_utils.money_from_float(value)

    def get_data(self, info):
        portfolio_sql_id = '1' if 'P_ITA01' in self.context.Title() else '0'
        data = self.umanot_utils.get_posts_by_portfolio(portfolio_sql_id, self.limit, self.min_date)

        performance = {'net_profit': None, 'drawdown': None, 'hit_rate': None, 'profit_factor': None}
        if data:
            latest = data[0]
            try:
                hit_rate = float(latest['win_op']) / (float(latest['los_op']) + float(latest['win_op'])) * 100
            except:
                hit_rate = 0

            performance['net_profit'] = str(latest['net_profit']).split('.')[0]
            performance['net_profit_open'] = str(latest['net_profit_open']).split('.')[0] if latest['net_profit_open'] else ''
            performance['drawdown'] = self.context.getLocation()  # latest['drawdown']
            performance['hit_rate'] = '%0.1f%%' % hit_rate if hit_rate else ''
            performance['profit_factor'] = '%.1f' % latest['profit_factor'] if latest['profit_factor'] else '--'

            last_value = 0
            counter = 0

            data.reverse()

            for x in data:
                if counter:
                    x['css_class'] = 'green' if float(x['net_profit']) >= last_value else 'red'
                    last_value = float(x['net_profit'])
                else:
                    x['css_class'] = 'green'
                counter += 1

            data.reverse()

        text = info['text']

        text = text.replace('$NET_PROFIT', performance['net_profit'])
        text = text.replace('$Net_Profit_Open', performance['net_profit_open'])
        text = text.replace('$DD_MAX', performance['drawdown'])
        text = text.replace('$HIT_RATE', performance['hit_rate'])
        text = text.replace('$PROFIT_FACTOR', performance['profit_factor'])

        info = dict(
            text = text,
            data = data,
            performance = performance
        )

        return info