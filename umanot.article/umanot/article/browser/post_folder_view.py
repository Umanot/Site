from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone.memoize.instance import memoize
from umanot.article.browser.interfaces import IPostPreFooter, IPostFooter, ILegenda, ILiveComment

from umanot.site.browser.umanot_utils import IUmanotUtils

from zope.component import getUtility
from zope.interface import implements, Interface
from zope.security import checkPermission


class IPostFolderView(Interface):
    """
    Article Forum Folder View view interface
    """


class PostFolderView(BrowserView):
    """
    Product browser view
    """
    implements(IPostFolderView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.limit = 2
        self.min_date = request.get('min_date', '')
        self.last_uid = request.get('last_uid')
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

    @property
    def can_edit(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    @memoize
    def legenda(self):
        brains = self.portal_catalog(
            portal_type = "Document",
            object_provides = ILegenda.__identifier__,
        )

        if not brains:
            return

        return brains[0].getObject().getText()

    @memoize
    def get_post_pre_footer(self):
        brains = self.portal_catalog(
            portal_type = "Document",
            object_provides = IPostPreFooter.__identifier__,
        )

        if not brains:
            return

        return brains[0].getObject().getText()

    @memoize
    def get_post_footer(self):
        brains = self.portal_catalog(
            portal_type = "Document",
            object_provides = IPostFooter.__identifier__,
        )

        if not brains:
            return

        return brains[0].getObject().getText()

    @property
    @memoize
    def contents(self):
        brains = self.portal_catalog(
            portal_type = ["Post"],
            path = '/'.join(self.context.getPhysicalPath()),
            sort_on = 'Date',
            sort_order = 'reverse',
        )

        uids = [brain.UID for brain in brains]

        if self.last_uid:
            try:
                show_more_index = uids.index(self.last_uid) + 1
            except ValueError:
                show_more_index = 0
        else:
            show_more_index = 0

        if show_more_index:
            brains = brains[show_more_index:]

        results = {'data': [], 'last_uid': None}

        counter = 0
        for brain in brains:
            if brain.exclude_from_nav:
                continue
            counter += 1
            obj = brain.getObject()
            info = obj.getInfo(scale = "original")

            info['section'] = obj.aq_parent.Title()
            info['other_images'] = obj.other_images()

            results['data'].append(info)

            if len(results['data']) == self.limit:
                break

        total_brains = len(brains)
        if results['data']:
            if counter == total_brains:
                results['last_uid'] = -1
            else:
                results['last_uid'] = results['data'][-1]['uid']

        return results

    def get_live_comment(self):
        brains = self.portal_catalog(
            portal_type = "Post",
            object_provides = ILiveComment.__identifier__
        )

        if not brains:
            return

        placeholder = brains[0].getObject().getInfo()

        try:
            portfolio_sql_id = '0'
            data = self.umanot_utils.get_posts_by_portfolio(portfolio_sql_id, self.limit, self.min_date)

            performance = {'net_profit': None, 'drawdown': None, 'hit_rate': None, 'profit_factor': None, 'total_op': None, 'win_op': None , 'lose_op': None, 'np_open': None}
            if data:
                latest = data[0]
                try:
                    hit_rate = float(latest['win_op']) / (float(latest['los_op']) + float(latest['win_op'])) * 100
                except:
                    hit_rate = 0

                performance['net_profit'] = str(latest['net_profit']).split('.')[0]
                performance['total_equity'] = str(latest['net_profit'] + 100000).split('.')[0]
                performance['net_profit_percentuale'] = '+ %.1f %%' % (latest['net_profit'] / float(100000) * 100)
                performance['drawdown'] = self.context.getLocation()  # latest['drawdown']
                performance['hit_rate'] = '%0.1f%%' % hit_rate if hit_rate else ''
                performance['profit_factor'] = '%.1f' % latest['profit_factor'] if latest['profit_factor'] else '--'
                #Added the following 4 variables in order to display them in the site- by Akbar - 7/12/2016
                #performance['win_op'] = '%.1f' % int(latest['win_op']) if int(latest['win_op']) else '--'
                performance['total_op'] = latest['tot_op'] if latest['tot_op'] else '--'
                performance['win_op'] = latest['win_op'] if latest['win_op'] else '--'
                performance['lose_op'] = latest['los_op'] if latest['los_op'] else '--'
                performance['np_open'] = latest['net_profit_open'] if latest['net_profit_open'] else '--'

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



            text = placeholder['text']

            text = text.replace('$NET_PROFIT_PERCENTUALE', performance['net_profit_percentuale'])
            text = text.replace('$NET_PROFIT', performance['net_profit'])
            text = text.replace('$TOTAL_EQUITY', performance['total_equity'])
            text = text.replace('$DD_MAX', performance['drawdown'])
            text = text.replace('$HIT_RATE', performance['hit_rate'])
            text = text.replace('$PROFIT_FACTOR', performance['profit_factor'])
            text = text.replace('$WIN_OP', performance['win_op'])

            info = dict(
                text = text,
                data = data,
                performance = performance
            )

            placeholder.update(info)
        except:
            pass

        return placeholder


    def get_data(self):
        portfolio_sql_id = 'portfolio-0'
        data = self.umanot_utils.get_posts_by_portfolio(portfolio_sql_id, self.limit, self.min_date)

        performance = {'net_profit': None, 'drawdown': None, 'hit_rate': None, 'profit_factor': None, 'total_op': None, 'win_op': None , 'lose_op': None, 'np_open': None}
        if data:
            latest = data[0]
            try:
                hit_rate = float(latest['win_op']) / (float(latest['los_op']) + float(latest['win_op'])) * 100
            except:
                hit_rate = 0

            performance['net_profit'] = str(latest['net_profit']).split('.')[0]

            performance['net_profit_percentuale'] = '+ %.1f %%' % (latest['net_profit'] / float(100000) * 100)
            performance['total_equity'] = str(latest['net_profit'] + 100000).split('.')[0]
            performance['net_profit_open'] = str(latest['net_profit_open']).split('.')[0] if latest['net_profit_open'] else ''
            performance['drawdown'] = self.context.getLocation()  # latest['drawdown']
            performance['hit_rate'] = '%0.1f %%' % hit_rate if hit_rate else ''
            performance['profit_factor'] = '%.1f' % latest['profit_factor'] if latest['profit_factor' \
                                                                                      ''] else '--'
            # Added the following 4 variables in order to display them in the site- by Akbar - 7/12/2016
            # performance['win_op'] = '%.1f' % int(latest['win_op']) if int(latest['win_op']) else '--'
            performance['total_op'] = latest['tot_op'] if latest['tot_op'] else '--'
            performance['win_op'] = latest['win_op'] if latest['win_op'] else '--'
            performance['lose_op'] = latest['los_op'] if latest['los_op'] else '--'
            performance['np_open'] = latest['net_profit_open'] if latest['net_profit_open'] else '--'

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

        text = self.contents['data'][0]['text'] if self.contents else ''

        text = text.replace('$NET_PROFIT_PERCENTUALE', performance['net_profit_percentuale'])
        text = text.replace('$NET_PROFIT', performance['net_profit'])
        text = text.replace('$TOTAL_EQUITY', performance['total_equity'])
        text = text.replace('$Net_Profit_Open', performance['net_profit_open'])
        text = text.replace('$DD_MAX', performance['drawdown'])
        text = text.replace('$HIT_RATE', performance['hit_rate'])
        text = text.replace('$PROFIT_FACTOR', performance['profit_factor'])
        # Accepted the following 4 variables as text in order to display them in the site- by Akbar - 7/12/2016
        text = text.replace('$TOTAL_OP', performance['total_op'])
        text = text.replace('$WIN_OP', performance['win_op'])
        text = text.replace('$LOSE_OP', performance['lose_op'])
        text = text.replace('$NP_OPEN', performance['np_open'])

        info = dict(
            text = text,
            data = data,
            performance = performance
        )

        return info