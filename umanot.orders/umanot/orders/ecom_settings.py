import persistent
from umanot.orders.browser.interfaces import IEcomSettings
from zope.interface import implements

class EcomSettings(persistent.Persistent):

    implements(IEcomSettings)

    cambio = 1.11933
    round_net = True
    threshold = 5