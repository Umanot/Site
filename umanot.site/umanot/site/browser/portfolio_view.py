from umanot.site.browser.umanot_utils import IUmanotUtils

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
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
        portfolios = ['portfolio-1', 'portfolio-2', 'portfolio-3']

        results = []

        for portfolio in portfolios:

            brains = self.portal_catalog(
                portal_type = "Post",
                getId = portfolio
            )

            if not brains:
                continue

            obj = brains[0].getObject()

            portfolio_sql_id = portfolio.split('-')[-1]
            data = self.umanot_utils.get_posts_by_portfolio(portfolio_sql_id, self.limit, self.min_date)

            performance = {'net_profit': None, 'drawdown': None, 'hit_rate': None, 'profit_factor': None}
            if data:
                latest = data[0]
                try:
                    hit_rate = float(latest['win_op']) / (float(latest['los_op']) + float(latest['win_op'])) * 100
                except:
                    hit_rate = 0

                performance['net_profit'] = latest['net_profit']
                performance['drawdown'] = obj.getLocation()  # latest['drawdown']
                performance['hit_rate'] = '%0.2f' % hit_rate if hit_rate else ''
                performance['profit_factor'] = latest['profit_factor']

                counter = 0
                for x in data:
                    counter += 1
                    prev = counter - 1
                    if prev:
                        self.context.plone_log("%s / %s" % (float(x['net_profit']), float(data[prev]['net_profit'])))
                        import pdb; pdb.set_trace()
                        x['css_class'] = 'green' if float(x['net_profit']) >= float(data[prev]['net_profit']) else 'red'
                    else:
                        x['css_class'] = 'green'

            info = dict(
                title = obj.Title(),
                description = obj.Description(),
                text = obj.getText(),
                data = data,
                performance = performance
            )

            results.append(info)

        return results
