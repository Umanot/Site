import itertools
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import implements, Interface

class IServiceFolderView(Interface):
    """
    Service view interface
    """


class ServiceFolderView(BrowserView):
    """
    Service browser view
    """
    implements(IServiceFolderView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.limit = 2
        self.min_date = request.get('min_date', '')

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')
        
    @property
    def title(self):
        return self.context.Title()
        
    @property
    def description(self):
        return self.context.Description()
        
    @property
    def contents(self):
        brains = self.portal_catalog(
            portal_type = ["Document", "Article", "Folder"],
            path = {'query':'/'.join(self.context.getPhysicalPath()) ,'depth': 1},
            sort_on = 'getObjPositionInParent',
            review_state = 'published'
        )

        results = []

        for brain in brains:
            if brain.exclude_from_nav:
                continue

            info = dict(
                title = brain.Title,
                description = self.get_description(brain),
                URL = brain.getURL()
            )

            results.append(info)

        results = self.grouper(3, results, None)

        return results

    def get_description(self, brain):
        description = brain.Description
        obj = brain.getObject()
        portfolio_sql_id = 'portfolio-1' if 'P_ITA01' in brain.Title else 'portfolio-0'

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
            performance['drawdown'] = obj.getLocation()  # latest['drawdown']
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

        description = description.replace('$NET_PROFIT', performance['net_profit'])
        description = description.replace('$Net_Profit_Open', performance['net_profit_open'])
        description = description.replace('$DD_MAX', performance['drawdown'])
        description = description.replace('$HIT_RATE', performance['hit_rate'])
        description = description.replace('$PROFIT_FACTOR', performance['profit_factor'])

        return description


    def grouper(self, n, iterable, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

class ZipExhausted(Exception):
    pass

def izip_longest(*args, **kwds):
    # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    fillvalue = kwds.get('fillvalue')
    counter = [len(args) - 1]
    def sentinel():
        if not counter[0]:
            raise ZipExhausted
        counter[0] -= 1
        yield fillvalue
    fillers = itertools.repeat(fillvalue)
    iterators = [itertools.chain(it, sentinel(), fillers) for it in args]
    try:
        while iterators:
            yield tuple(map(next, iterators))
    except ZipExhausted:
        pass