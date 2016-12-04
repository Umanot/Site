from umanot.site.browser.umanot_utils import IUmanotUtils

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone import api
from zope.component import getUtility
from zope.interface import implements, Interface


class IPortfolioView(Interface):
    """
    Article Folder View view interface
    """


class PortfolioView(BrowserView):
    """
    Product browser view
    """
    implements(IPortfolioView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.limit = request.get('limit', '')
        self.min_date = request.get('min_date', '')
        self.umanot_utils = getUtility(IUmanotUtils)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()

    def get_data(self):
        user = api.user.get_current()

        user_data = user.getProperty('description')
        if not user_data:
            return

        portfolios = user_data.split('\n')

        results = []

        root_obj = api.portal.get_navigation_root(self.context)

        for portfolio in portfolios:
            portfolio_id, portfolio_title = portfolio.split('|')

            brains = self.portal_catalog.unrestrictedSearchResults(
                portal_type = "Post",
                path = '/'.join(root_obj.getPhysicalPath()),
                getId = portfolio_id
            )

            if not brains:
                continue

            obj = self.context.unrestrictedTraverse(brains[0].getPath())

            portfolio_sql_id = portfolio_id.split('-')[-1]
            if portfolio_sql_id in ['2', '3']:
                portfolio_sql_id = '1'

            data = self.umanot_utils.get_posts_by_portfolio(portfolio_sql_id, self.limit, self.min_date)

            performance = {'net_profit': None, 'drawdown': None, 'hit_rate': None, 'profit_factor': None, 'win_op': None}
            if data:
                latest = data[0]
                try:
                    hit_rate = float(latest['win_op']) / (float(latest['los_op']) + float(latest['win_op'])) * 100
                except:
                    hit_rate = 0

                performance['net_profit'] = str(latest['net_profit']).split('.')[0]
                performance['total_equity'] = str(latest['net_profit'] + 100000).split('.')[0]
                performance['net_profit_percentuale'] = '+ %.1f %%' % (latest['net_profit'] / float(100000) * 100)
                performance['net_profit_open'] = str(latest['net_profit_open']).split('.')[0] if latest['net_profit_open'] else ''
                performance['drawdown'] = obj.getLocation()  # latest['drawdown']
                performance['hit_rate'] = '%0.1f%%' % hit_rate if hit_rate else ''
                performance['profit_factor'] = '%.1f' % latest['profit_factor'] if latest['profit_factor'] else '--'
                performance['win_op'] = '%.1f' % latest['win_op'] if latest['win_op'] else '--'

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

            text = obj.getText()

            text = text.replace('$NET_PROFIT_PERCENTUALE', performance['net_profit_percentuale'])
            text = text.replace('$NET_PROFIT', performance['net_profit'])
            text = text.replace('$TOTAL_EQUITY', performance['total_equity'])
            text = text.replace('$Net_Profit_Open', performance['net_profit_open'])
            text = text.replace('$DD_MAX', performance['drawdown'])
            text = text.replace('$HIT_RATE', performance['hit_rate'])
            text = text.replace('$PROFIT_FACTOR', performance['profit_factor'])
            text = text.replace('$WIN_OP', performance['win_op'])

            info = dict(
                title = portfolio_title,
                description = obj.Description(),
                text = text,
                data = data,
                performance = performance
            )

            results.append(info)

        return results
