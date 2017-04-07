from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone.api import user
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
            performance = {'net_profit': None, 'drawdown': None, 'hit_rate': None, 'profit_factor': None, 'total_op': None, 'win_op': None, 'lose_op': None, 'open_op': None,'net_profit_open': None, 'net_profit_3': None, 'drawdown_3': None, 'hit_rate_3': None, 'profit_factor_3': None, 'total_op_3': None, 'win_op_3': None, 'lose_op_3': None, 'open_op_3': None,'net_profit_open_3': None, 'net_profit_4': None, 'drawdown_4': None, 'hit_rate_4': None, 'profit_factor_4': None, 'total_op_4': None, 'win_op_4': None, 'lose_op_4': None, 'open_op_4': None,'net_profit_open_4': None}

            # performance = {'net_profit': None, 'drawdown': None, 'hit_rate': None, 'profit_factor': None, 'total_op': None, 'win_op': None, 'lose_op': None, 'open_op': None,'net_profit_open': None}
            if data:
                latest = data[0]
                latest_3 = data[1]
                latest_4 = data[1]
                try:
                    hit_rate = float(latest['win_op']) / (float(latest['los_op']) + float(latest['win_op'])) * 100
                    hit_rate_3 = float(latest_3['win_op']) / (float(latest_3['los_op']) + float(latest_3['win_op'])) * 100
                    hit_rate_4 = float(latest_4['win_op']) / (float(latest_4['los_op']) + float(latest_4['win_op'])) * 100
                except:
                    hit_rate = 0
                    hit_rate_3 = 0
                    hit_rate_4 = 0

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
                # Added one more variable(open_op) in order to display them in the site- by Akbar - 16/12/2016
                performance['open_op'] = latest['open_op'] if latest['open_op'] else '--'
                performance['net_profit_open'] = str(latest['net_profit_open']).split('.')[0] if latest['net_profit_open'] else ''

                """"
                # for STM stock
              performance['net_profit_2'] = str(latest_2['net_profit']).split('.')[0]
                performance['total_equity_2'] = str(latest_2['net_profit'] + 100000).split('.')[0]
                performance['net_profit_percentuale_2'] = '+ %.1f %%' % (latest_2['net_profit'] / float(100000) * 100)
                performance['drawdown_2'] = self.context.getLocation()  # latest['drawdown']
                performance['hit_rate_2'] = '%0.1f%%' % hit_rate_2 if hit_rate_2 else ''
                performance['profit_factor_2'] = '%.1f' % latest_2['profit_factor'] if latest_2['profit_factor'] else '--'
                # Added the following 4 variables in order to display them in the site- by Akbar - 7/12/2016
                # performance['win_op'] = '%.1f' % int(latest['win_op']) if int(latest['win_op']) else '--'
                performance['total_op_2'] = latest_2['tot_op'] if latest_2['tot_op'] else '--'
                performance['win_op_2'] = latest_2['win_op'] if latest_2['win_op'] else '--'
                performance['lose_op_2'] = latest_2['los_op'] if latest_2['los_op'] else '--'
                # Added one more variable(open_op) in order to display them in the site- by Akbar - 16/12/2016
                performance['open_op_2'] = latest_2['open_op'] if latest_2['open_op'] else '--'
                performance['net_profit_open_2'] = str(latest_2['net_profit_open']).split('.')[0] if latest_2['net_profit_open'] else ''
                """

                # for ISP stock
                performance['net_profit_3'] = str(latest_3['net_profit']).split('.')[0]
                performance['total_equity_3'] = str(latest_3['net_profit'] + 100000).split('.')[0]
                performance['net_profit_percentuale_3'] = '+ %.1f %%' % (latest_3['net_profit'] / float(100000) * 100)
                performance['drawdown_3'] = self.context.getLocation()  # latest['drawdown']
                performance['hit_rate_3'] = '%0.1f%%' % hit_rate_3 if hit_rate_3 else ''
                performance['profit_factor_3'] = '%.1f' % latest_3['profit_factor'] if latest_3['profit_factor'] else '--'
                # Added the following 4 variables in order to display them in the site- by Akbar - 7/12/2016
                # performance['win_op'] = '%.1f' % int(latest['win_op']) if int(latest['win_op']) else '--'
                performance['total_op_3'] = latest_3['tot_op'] if latest_3['tot_op'] else '--'
                performance['win_op_3'] = latest_3['win_op'] if latest_3['win_op'] else '--'
                performance['lose_op_3'] = latest_3['los_op'] if latest_3['los_op'] else '--'
                # Added one more variable(open_op) in order to display them in the site- by Akbar - 16/12/2016
                performance['open_op_3'] = latest_3['open_op'] if latest_3['open_op'] else '--'
                performance['net_profit_open_3'] = str(latest_3['net_profit_open']).split('.')[0] if latest_3['net_profit_open'] else ''

                # for ENEL stock
                performance['net_profit_4'] = str(latest_4['net_profit']).split('.')[0]
                performance['total_equity_4'] = str(latest_4['net_profit'] + 100000).split('.')[0]
                performance['net_profit_percentuale_4'] = '+ %.1f %%' % (latest_4['net_profit'] / float(100000) * 100)
                performance['drawdown_4'] = self.context.getLocation()  # latest['drawdown']
                performance['hit_rate_4'] = '%0.1f%%' % hit_rate_4 if hit_rate_4 else ''
                performance['profit_factor_4'] = '%.1f' % latest_4['profit_factor'] if latest_4[ 'profit_factor'] else '--'
                # Added the following 4 variables in order to display them in the site- by Akbar - 7/12/2016
                # performance['win_op'] = '%.1f' % int(latest['win_op']) if int(latest['win_op']) else '--'
                performance['total_op_4'] = latest_4['tot_op'] if latest_4['tot_op'] else '--'
                performance['win_op_4'] = latest_4['win_op'] if latest_4['win_op'] else '--'
                performance['lose_op_4'] = latest_4['los_op'] if latest_4['los_op'] else '--'
                # Added one more variable(open_op) in order to display them in the site- by Akbar - 16/12/2016
                performance['open_op_4'] = latest_4['open_op'] if latest_4['open_op'] else '--'
                performance['net_profit_open_4'] = str(latest_4['net_profit_open']).split('.')[0] if latest_4['net_profit_open'] else ''

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
            text = text.replace('$NET_PROFIT_OPEN', str(performance['net_profit_open']))
            text = text.replace('$NET_PROFIT', performance['net_profit'])
            text = text.replace('$TOTAL_EQUITY', performance['total_equity'])
            text = text.replace('$DD_MAX', performance['drawdown'])
            text = text.replace('$HIT_RATE', performance['hit_rate'])
            text = text.replace('$PROFIT_FACTOR', performance['profit_factor'])
            # Accepted the following 4 variables as text in order to display them in the site- by Akbar - 7/12/2016
            # text = text.replace('$TOTAL_OP', performance['total_op'])
            text = text.replace('$WIN_OP', str(performance['win_op']))
            text = text.replace('$LOSE_OP', str(performance['lose_op']))


            text = text.replace('$TOTAL_OP', str(performance['total_op']))
            text = text.replace('$LOSE_OP', str(performance['lose_op']))
            # Added one more variable(open_op) as text in order to display them in the site- by Akbar - 16/12/2016
            text = text.replace('$OPEN_OP', str(performance['open_op']))

            """
            # for STM stock
            text = text.replace('$NET_PROFIT_PERCENTUALE_2', performance['net_profit_percentuale_2'])
            text = text.replace('$NET_PROFIT_OPEN_2', str(performance['net_profit_open_2']))
            text = text.replace('$NET_PROFIT_2', performance['net_profit_2'])
            text = text.replace('$TOTAL_EQUITY_2', performance['total_equity_2'])
            text = text.replace('$DD_MAX_2', performance['drawdown_2'])
            text = text.replace('$HIT_RATE_2', performance['hit_rate_2'])
            text = text.replace('$PROFIT_FACTOR_2', performance['profit_factor_2'])
            # Accepted the following 4 variables as text in order to display them in the site- by Akbar - 7/12/2016
            # text = text.replace('$TOTAL_OP', performance['total_op'])
            text = text.replace('$WIN_OP_2', str(performance['win_op_2']))
            text = text.replace('$LOSE_OP_2', str(performance['lose_op_2']))

            text = text.replace('$TOTAL_OP_2', str(performance['total_op_2']))
            text = text.replace('$LOSE_OP_2', str(performance['lose_op_2']))
            # Added one more variable(open_op) as text in order to display them in the site- by Akbar - 16/12/2016
            text = text.replace('$OPEN_OP_2', str(performance['open_op_2']))
            """
            # for ISP stock
            text = text.replace('$NET_PROFIT_PERCENTUALE_3', performance['net_profit_percentuale_3'])
            text = text.replace('$NET_PROFIT_OPEN_3', str(performance['net_profit_open_3']))
            text = text.replace('$NET_PROFIT_3', performance['net_profit_3'])
            text = text.replace('$TOTAL_EQUITY_3', performance['total_equity_3'])
            text = text.replace('$DD_MAX_3', performance['drawdown_3'])
            text = text.replace('$HIT_RATE_3', performance['hit_rate_3'])
            text = text.replace('$PROFIT_FACTOR_3', performance['profit_factor_3'])
            # Accepted the following 4 variables as text in order to display them in the site- by Akbar - 7/12/2016
            # text = text.replace('$TOTAL_OP', performance['total_op'])
            text = text.replace('$WIN_OP_3', str(performance['win_op_3']))
            text = text.replace('$LOSE_OP_3', str(performance['lose_op_3']))

            text = text.replace('$TOTAL_OP_3', str(performance['total_op_3']))
            text = text.replace('$LOSE_OP_3', str(performance['lose_op_3']))
            # Added one more variable(open_op) as text in order to display them in the site- by Akbar - 16/12/2016
            text = text.replace('$OPEN_OP_3', str(performance['open_op_3']))

            # for ENEL stock
            text = text.replace('$NET_PROFIT_PERCENTUALE_4', performance['net_profit_percentuale_4'])
            text = text.replace('$NET_PROFIT_OPEN_4', str(performance['net_profit_open_4']))
            text = text.replace('$NET_PROFIT_4', performance['net_profit_4'])
            text = text.replace('$TOTAL_EQUITY_4', performance['total_equity_4'])
            text = text.replace('$DD_MAX_4', performance['drawdown_4'])
            text = text.replace('$HIT_RATE_4', performance['hit_rate_4'])
            text = text.replace('$PROFIT_FACTOR_4', performance['profit_factor_4'])
            # Accepted the following 4 variables as text in order to display them in the site- by Akbar - 7/12/2016
            # text = text.replace('$TOTAL_OP', performance['total_op'])
            text = text.replace('$WIN_OP_4', str(performance['win_op_4']))
            text = text.replace('$LOSE_OP_4', str(performance['lose_op_4']))

            text = text.replace('$TOTAL_OP_4', str(performance['total_op_4']))
            text = text.replace('$LOSE_OP_4', str(performance['lose_op_4']))
            # Added one more variable(open_op) as text in order to display them in the site- by Akbar - 16/12/2016
            text = text.replace('$OPEN_OP_4', str(performance['open_op_4']))

            placeholder['operazioni'] = placeholder['operazioni'].replace('$TOTAL_OP', str(performance['total_op']))
            placeholder['operazioni_12'] = placeholder['operazioni_12'].replace('$WIN_OP', str(performance['win_op'])).replace('$LOSE_OP', str(performance['lose_op']))
            placeholder['operazioni_1x2'] = placeholder['operazioni_1x2'].replace('$OPEN_OP', str(performance['open_op']))  # @ AKBAR PUT THE OPEN_OP REPLACEMENTE HERE. REMEMBER TO CAST NUMBER TO STRING
            placeholder['operazioni_1x3'] = placeholder['operazioni_1x3'].replace('$NET_PROFIT', str(performance['net_profit']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_1x4'] = placeholder['operazioni_1x4'].replace('$NET_PROFIT_OPEN', str(performance['net_profit_open']))  # 4/4/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_1x5'] = placeholder['operazioni_1x5'].replace('$DD_MAX', str(performance['drawdown']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_1x6'] = placeholder['operazioni_1x6'].replace('$PROFIT_FACTOR', str(performance['profit_factor']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_1x7'] = placeholder['operazioni_1x7'].replace('$HIT_RATE', str(performance['hit_rate']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box

            """
            # for STM stock
            placeholder['operazioni_2'] = placeholder['operazioni_2'].replace('$TOTAL_OP_2', str(performance['total_op_2']))
            placeholder['operazioni_22'] = placeholder['operazioni_22'].replace('$WIN_OP_2', str(performance['win_op_2'])).replace('$LOSE_OP_2', str(performance['lose_op_2']))
            placeholder['operazioni_2x2'] = placeholder['operazioni_2x2'].replace('$OPEN_OP_2', str(performance['open_op_2']))  # @ AKBAR PUT THE OPEN_OP REPLACEMENTE HERE. REMEMBER TO CAST NUMBER TO STRING
            placeholder['operazioni_2x3'] = placeholder['operazioni_2x3'].replace('$NET_PROFIT_2', str(performance['net_profit_2']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_2x4'] = placeholder['operazioni_2x4'].replace('$NET_PROFIT_OPEN_2', str(performance['net_profit_open_2']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_2x5'] = placeholder['operazioni_2x5'].replace('$DD_MAX_2', str(performance['drawdown_2']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_2x6'] = placeholder['operazioni_2x6'].replace('$PROFIT_FACTOR_2', str(performance['profit_factor_2']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_2x7'] = placeholder['operazioni_2x7'].replace('$HIT_RATE_2', str(performance['hit_rate_2'])) # 26/3/17 @ Added by AKBAR for enhancing the blue box
            """
            # for STM stock
            placeholder['operazioni_3'] = placeholder['operazioni_3'].replace('$TOTAL_OP_3', str(performance['total_op_3']))
            placeholder['operazioni_32'] = placeholder['operazioni_32'].replace('$WIN_OP_3', str(performance['win_op_3'])).replace('$LOSE_OP_3', str(performance['lose_op_3']))
            placeholder['operazioni_3x2'] = placeholder['operazioni_3x2'].replace('$OPEN_OP_3', str(performance['open_op_3']))  # @ AKBAR PUT THE OPEN_OP REPLACEMENTE HERE. REMEMBER TO CAST NUMBER TO STRING
            placeholder['operazioni_3x3'] = placeholder['operazioni_3x3'].replace('$NET_PROFIT_3', str(performance['net_profit_3']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_3x4'] = placeholder['operazioni_3x4'].replace('$NET_PROFIT_OPEN_3', str(performance['net_profit_open_3']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_3x5'] = placeholder['operazioni_3x5'].replace('$DD_MAX_3', str(performance['drawdown_3']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_3x6'] = placeholder['operazioni_3x6'].replace('$PROFIT_FACTOR_3', str(performance['profit_factor_3']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_3x7'] = placeholder['operazioni_3x7'].replace('$HIT_RATE_3', str(performance['hit_rate_3']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box

            # for ENEL stock
            placeholder['operazioni_4'] = placeholder['operazioni_4'].replace('$TOTAL_OP_4', str(performance['total_op_4']))
            placeholder['operazioni_42'] = placeholder['operazioni_42'].replace('$WIN_OP_4', str(performance['win_op_4'])).replace('$LOSE_OP_4', str(performance['lose_op_4']))
            placeholder['operazioni_4x2'] = placeholder['operazioni_4x2'].replace('$OPEN_OP_4', str(performance['open_op_4']))  # @ AKBAR PUT THE OPEN_OP REPLACEMENTE HERE. REMEMBER TO CAST NUMBER TO STRING
            placeholder['operazioni_4x3'] = placeholder['operazioni_4x3'].replace('$NET_PROFIT_4', str(performance['net_profit_4']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_4x4'] = placeholder['operazioni_4x4'].replace('$NET_PROFIT_OPEN_4', str(performance['net_profit_open_4']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_4x5'] = placeholder['operazioni_4x5'].replace('$DD_MAX_4', str(performance['drawdown_4']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_4x6'] = placeholder['operazioni_4x6'].replace('$PROFIT_FACTOR_4', str(performance['profit_factor_4']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box
            placeholder['operazioni_4x7'] = placeholder['operazioni_4x7'].replace('$HIT_RATE_4', str(performance['hit_rate_4']))  # 26/3/17 @ Added by AKBAR for enhancing the blue box

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

        performance = {'net_profit': None, 'drawdown': None, 'hit_rate': None, 'profit_factor': None, 'total_op': None, 'win_op': None , 'lose_op': None, 'open_op': None, 'net_profit_open': None}
        if data:
            latest = data[0]
            try:
                hit_rate = float(latest['win_op']) / (float(latest['los_op']) + float(latest['win_op'])) * 100
            except:
                hit_rate = 0

            performance['net_profit'] = str(latest['net_profit']).split('.')[0]
            performance['net_profit_percentuale'] = '+ %.1f %%' % (latest['net_profit'] / float(100000) * 100)
            performance['total_equity'] = str(latest['net_profit'] + 100000).split('.')[0]
            performance['drawdown'] = self.context.getLocation()  # latest['drawdown']
            performance['hit_rate'] = '%0.1f %%' % hit_rate if hit_rate else ''
            performance['profit_factor'] = '%.1f' % latest['profit_factor'] if latest['profit_factor'] else '--'
            # Added the following 4 variables in order to display them in the site- by Akbar - 7/12/2016
            # performance['win_op'] = '%.1f' % int(latest['win_op']) if int(latest['win_op']) else '--'
            performance['total_op'] = latest['tot_op'] if latest['tot_op'] else '--'
            performance['win_op'] = latest['win_op'] if latest['win_op'] else '--'
            performance['lose_op'] = latest['los_op'] if latest['los_op'] else '--'
            # Added one more variable(open_op) in order to display them in the site- by Akbar - 16/12/2016
            performance['open_op'] = latest['open_op'] if latest['open_op'] else '--'
            performance['net_profit_open'] = str(latest['net_profit_open']).split('.')[0] if latest['net_profit_open'] else ''

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
        text = text.replace('$DD_MAX', performance['drawdown'])
        text = text.replace('$HIT_RATE', performance['hit_rate'])
        text = text.replace('$PROFIT_FACTOR', performance['profit_factor'])
        # Accepted the following 4 variables as text in order to display them in the site- by Akbar - 7/12/2016
        text = text.replace('$TOTAL_OP', str(performance['total_op']))
        text = text.replace('$WIN_OP', str(performance['win_op']))
        text = text.replace('$LOSE_OP', str(performance['lose_op']))
        # Added one more variable(open_op) as text in order to display them in the site- by Akbar - 16/12/2016
        text = text.replace('$OPEN_OP', str(performance['open_op']))
        text = text.replace('$NET_PROFIT_OPEN', str(performance['net_profit_open']))

        info = dict(
            text = text,
            data = data,
            performance = performance
        )

        return info