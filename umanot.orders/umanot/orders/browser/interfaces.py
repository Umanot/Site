from zope.interface import Interface
from zope import schema


class IEcomSettings(Interface):
    """Ecom Settings.
    """

    cambio = schema.Float(
        title = u"Cambioeuro/dollaro",
        required = True,
        default = 1.11933
    )