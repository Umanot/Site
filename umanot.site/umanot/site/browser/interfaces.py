from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Umanot - SitePackage" theme, this interface must be its layer
       (in site/viewlets/configure.zcml).
    """

class IHomepageServices(Interface):
    """Marker interface"""


class IHomepageSecondLine(Interface):
    """Marker interface"""